import pytest
import os
from cyprus.core.prolog_engine import PrologEngine

def test_assert_and_query(engine):
    """Test asserting a fact and querying it."""
    engine.assertz("father(john, pete)")
    solutions = engine.query("father(john, X)")
    assert solutions == [{'X': 'pete'}]

def test_load_file(engine):
    """Test loading a Prolog file and querying its contents."""
    # Create a dummy prolog file
    prolog_content = "mother(jane, pete)."
    file_path = "/home/czar/code/cyprus/tests/test_rules.pl"
    with open(file_path, "w") as f:
        f.write(prolog_content)

    engine.load_file(file_path)
    solutions = engine.query("mother(jane, X)")
    assert solutions == [{'X': 'pete'}]

    # Clean up the dummy file
    os.remove(file_path)

def test_query_no_solution(engine):
    """Test a query that should have no solution."""
    solutions = engine.query("non_existent_fact(a,b)")
    assert solutions == []

def test_retract(engine):
    """Test retracting a fact."""
    engine.assertz("friend(a,b)")
    assert engine.query("friend(a,b)") != []
    engine.retractall("friend(_,_)")
    assert engine.query("friend(a,b)") == []
