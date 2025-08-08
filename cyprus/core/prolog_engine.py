from pyswip import Prolog
import tempfile
import os

class PrologEngine:
    """
    A wrapper around a Prolog engine to manage facts, rules, and queries.
    """
    def __init__(self):
        self.prolog = Prolog()

    def load_file(self, file_path: str):
        """
        Consults a Prolog file.

        Args:
            file_path: The path to the .pl file.
        """
        try:
            self.prolog.consult(file_path)
        except Exception as e:
            print(f"Error consulting Prolog file {file_path}: {e}")
            raise

    def consult_string(self, rules: str):
        """
        Consults a string of Prolog rules.
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pl") as f:
            f.write(rules)
            temp_path = f.name
        
        try:
            self.load_file(temp_path)
        finally:
            os.remove(temp_path)


    def assertz(self, fact: str):
        """
        Asserts a fact into the Prolog database.

        Args:
            fact: The fact string to assert (e.g., "model(gpt4, org(openai))").
        """
        self.prolog.assertz(fact)

    def query(self, query_string: str) -> list:
        """
        Executes a query and returns all solutions.

        Args:
            query_string: The query to execute (e.g., "restricted(Model)").

        Returns:
            A list of solutions, where each solution is a dictionary.
            Returns an empty list if there are no solutions.
        """
        try:
            solutions = list(self.prolog.query(query_string))
            return solutions
        except Exception as e:
            print(f"Error executing Prolog query '{query_string}': {e}")
            return []

    def retractall(self, fact: str):
        """
        Retracts all matching facts from the Prolog database.

        Args:
            fact: The fact pattern to retract (e.g., "model(_,_,_,_)").
        """
        self.prolog.retractall(fact)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        A placeholder for cleanup. The underlying Prolog threads are managed
        by the pyswip process.
        """
        pass
