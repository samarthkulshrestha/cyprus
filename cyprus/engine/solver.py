from pathlib import Path
from datetime import datetime

import clingo
import yaml

from cyprus.engine.result import (
    ComplianceResult,
    ComplianceStatus,
    ModelCompliance,
    Violation,
)


class Solver:
    """
    Wraps the Clingo ASP solver for compliance evaluation.

    Usage:
        solver = Solver(policy_dir=Path("cyprus/policies/eu_ai_act"))
        solver.load_model_facts(facts_string)
        result = solver.solve()
    """

    def __init__(self, policy_dir: Path) -> None:
        self._policy_dir = policy_dir
        self._model_facts: str = ""
        self._manifest = self._load_manifest()
        self._rule_files = self._discover_rules()

    def _load_manifest(self) -> dict:
        """Load and validate manifest.yaml from the policy directory."""
        manifest_path = self._policy_dir / "manifest.yaml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"manifest.yaml not found in {self._policy_dir}")
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        for field in ("name", "version", "articles_covered", "output_predicates"):
            if field not in manifest:
                raise ValueError(f"manifest.yaml missing required field: {field}")
        return manifest

    def _discover_rules(self) -> list[Path]:
        """Find all .lp files in the rules/ subdirectory."""
        rules_dir = self._policy_dir / "rules"
        if not rules_dir.exists():
            raise FileNotFoundError(f"rules/ directory not found in {self._policy_dir}")
        return sorted(rules_dir.glob("*.lp"))

    def load_model_facts(self, facts: str) -> None:
        """Load ASP fact string representing model data."""
        self._model_facts = facts

    def solve(self) -> ComplianceResult:
        """
        Run the ASP solver and return typed compliance results.

        Grounds all rule files + model facts, computes stable models,
        and parses the answer set into ComplianceResult.
        """
        ctl = clingo.Control(["0"])

        # Load all rule files
        for rule_file in self._rule_files:
            ctl.load(str(rule_file))

        # Add model facts
        ctl.add("base", [], self._model_facts)

        # Ground
        ctl.ground([("base", [])])

        # Solve and collect atoms
        atoms: list[clingo.Symbol] = []
        with ctl.solve(yield_=True) as handle:
            for model in handle:
                atoms = list(model.symbols(shown=True))

        # Parse atoms into ComplianceResult
        return self._parse_answer_set(atoms)

    def _parse_answer_set(self, atoms: list[clingo.Symbol]) -> ComplianceResult:
        """Parse raw Clingo atoms into typed ComplianceResult."""
        model_ids: set[str] = set()
        prohibited: dict[str, list[Violation]] = {}
        unmet: dict[str, list[Violation]] = {}
        systemic: set[str] = set()
        high_risk: set[str] = set()
        transparency: set[str] = set()
        deployable: set[str] = set()

        for atom in atoms:
            name = atom.name
            args = atom.arguments

            if name == "model" and len(args) == 1:
                mid = str(args[0])
                model_ids.add(mid)

            elif name == "prohibited" and len(args) == 3:
                mid = str(args[0])
                article = str(args[1])
                reason = str(args[2]).strip('"')
                prohibited.setdefault(mid, []).append(
                    Violation(article=article, title=article, reason=reason, severity="prohibited")
                )

            elif name == "systemic_risk" and len(args) == 2:
                systemic.add(str(args[0]))

            elif name == "requires_high_risk_compliance" and len(args) == 2:
                high_risk.add(str(args[0]))

            elif name == "requires_transparency" and len(args) == 2:
                transparency.add(str(args[0]))

            elif name == "unmet_requirement" and len(args) == 2:
                mid = str(args[0])
                reason = str(args[1]).strip('"')
                unmet.setdefault(mid, []).append(
                    Violation(article="", title="", reason=reason, severity="required")
                )

            elif name == "can_deploy" and len(args) == 1:
                deployable.add(str(args[0]))

        # Build per-model results
        models: dict[str, ModelCompliance] = {}
        for mid in model_ids:
            is_prohibited = mid in prohibited
            is_deployable = mid in deployable

            if is_prohibited:
                status = ComplianceStatus.PROHIBITED
            elif not is_deployable and mid in unmet:
                status = ComplianceStatus.REQUIRES_ACTION
            elif is_deployable:
                status = ComplianceStatus.COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT

            models[mid] = ModelCompliance(
                model_id=mid,
                status=status,
                prohibited=prohibited.get(mid, []),
                unmet_requirements=unmet.get(mid, []),
                systemic_risk=mid in systemic,
                high_risk=mid in high_risk,
                transparency_required=mid in transparency,
                can_deploy=is_deployable,
            )

        return ComplianceResult(
            models=models,
            policy_name=self._manifest["name"],
            policy_version=self._manifest["version"],
            timestamp=datetime.now(),
            articles_evaluated=[a["id"] for a in self._manifest["articles_covered"]],
        )

    def explain(self, model_id: str) -> list[Violation]:
        """Return all violations and unmet requirements for a specific model."""
        result = self.solve()
        if model_id not in result.models:
            raise ValueError(f"Model '{model_id}' not found in results")
        mc = result.models[model_id]
        return mc.prohibited + mc.unmet_requirements
