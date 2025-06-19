import unittest

__all__ = ["test"]


def test() -> unittest.TextTestRunner:
    "This function runs all the tests."
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir="felice.tests")
    runner = unittest.TextTestRunner()
    result = runner.run(tests)
    return result
