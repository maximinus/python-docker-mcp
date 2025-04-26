import unittest 
from pathlib import Path

from environment import (get_venv_path,
                         check_pip_exists,
                         get_package_list,
                         get_all_packages)


EXAMPLE_PATH = Path.cwd()


class TestEnvironment(unittest.TestCase):
    def test_get_path_works(self):
        get_venv_path(EXAMPLE_PATH)

    def test_fake_path_fails(self):
        with self.assertRaises(FileNotFoundError):
            get_venv_path(Path('/fake/path'))

    def test_get_venv_path_found(self):
        expected_path = EXAMPLE_PATH / 'venv' / 'bin' / 'python'
        self.assertEqual(get_venv_path(EXAMPLE_PATH), expected_path)

    def test_check_pip_exists_true(self):
        pip_folder = get_venv_path(EXAMPLE_PATH)
        self.assertTrue(check_pip_exists(pip_folder))

    def test_check_pip_exists_false(self):
        self.assertFalse(check_pip_exists(Path('/fake/path')))

    def test_package_list(self):
        package_list = get_package_list(EXAMPLE_PATH)
        self.assertTrue(len(package_list) > 0)

    def test_get_packages_is_single(self):
        packages = get_all_packages(EXAMPLE_PATH)
        self.assertTrue(len(packages) > 0)
    
    def test_package_versions(self):
        packages = get_all_packages(EXAMPLE_PATH)
        for package in packages:
            version_numbers = package.version.split('.')
            # this will raise an error if the version is not a number
            [int(x) for x in version_numbers]


if __name__ == '__main__':
    unittest.main()
