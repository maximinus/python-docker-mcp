import os

from enum import Enum, auto


class TestType(Enum):
    PYTEST = auto()
    UNITTEST = auto()
    UNKNOWN = auto()


def is_pytest(content: str):
    return "import pytest" in content or "@pytest.mark" in content or "def test_" in content

def is_unittest(content: str):
    return "import unittest" in content or "unittest.TestCase" in content


def detect_test_type(path: str) -> TestType:
    paths_to_check = []
    if os.path.isfile(path):
        paths_to_check.append(path)
    else:
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    paths_to_check.append(os.path.join(root, file))

    for file_path in paths_to_check:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if is_pytest(content):
                    return TestType.PYTEST
                if is_unittest(content):
                    return TestType.UNITTEST
        except Exception:
            continue

    return TestType.UNKNOWN
