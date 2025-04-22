from mcp.server.fastmcp import FastMCP

from test_detector import detect_test_type, TestType

mcp = FastMCP('python-docker-mcp')


@mcp.tool()
def run_code(filepath: str) -> str:
    """
    Run the file found at filepath, which is local to the project and a python file
    The function will run the file on the command line with "python filepath"
    It will return the output (stdout and stderr)
    """
    return run_in_docker(f"python {filepath}")

@mcp.tool()
def run_tests(folder: str) -> str:
    """
    Run the tests found in the folder
    The folder is a path to a local folder that contains tests
    The tests can be unittest or pytest files
    It will return the output of the tests
    """
    test_type = detect_test_type(folder)
    if test_type == TestType.PYTEST:
        return run_in_docker(f"pytest {folder}")
    elif test_type == TestType.UNITTEST:
        return run_in_docker(f"python -m unittest discover -s {folder}")
    else:
        return f"Unable to detect test framework in {folder}"

@mcp.tool()
def run_test_file(filepath: str) -> str:
    """
    Run the test file found at filepath
    The file is a path to a local file that contains tests
    It will return the output of the tests
    """
    test_type = detect_test_type(filepath)
    if test_type == TestType.PYTEST:
        return run_in_docker(f"pytest {filepath}")
    elif test_type == TestType.UNITTEST:
        return run_in_docker(f"python -m unittest {filepath}")
    else:
        return f"Unable to detect test framework in {filepath}"

@mcp.tool()
def run_single_test(filepath: str, test_name: str) -> str:
    """
    Run a single test
    The filepath is a path to a local file that contains tests
    The test_name is the name of the test to run
    It will return the output of the test
    """
    test_type = detect_test_type(filepath)
    if test_type == TestType.PYTEST:
        return run_in_docker(f"pytest {filepath}::{test_name}")
    elif test_type == TestType.UNITTEST:
        return run_in_docker(f"python -m unittest {filepath}.{test_name}")
    else:
        return f"Unable to detect test framework in {filepath}"
