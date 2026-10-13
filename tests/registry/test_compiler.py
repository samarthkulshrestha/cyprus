from cyprus.registry.compiler import compile_models


def test_compile_single_model(compliant_model):
    facts = compile_models([compliant_model])

    assert "model(test_compliant)." in facts
    assert 'model_attr(test_compliant, organization, "TestOrg").' in facts
    assert "model_attr(test_compliant, use_case, general_purpose)." in facts
    assert "model_attr(test_compliant, deployment_region, eu)." in facts
    assert "model_attr(test_compliant, capability, chat)." in facts
    assert "model_governance(test_compliant, training_data_quality, 95)." in facts


def test_compile_multiple_models(compliant_model, prohibited_model):
    facts = compile_models([compliant_model, prohibited_model])

    assert "model(test_compliant)." in facts
    assert "model(test_prohibited)." in facts


def test_compile_empty():
    facts = compile_models([])
    assert facts == ""
