import subprocess
from pathlib import Path

from dataclasses import dataclass


@dataclass
class Package:
    name: str
    version: str


def get_venv_path(project_path: Path) -> Path:
    for i in ['venv', '.venv', 'venv3', '.venv3']:
        if (project_path / i).exists():
            bin_path = project_path / i / 'bin'
            if bin_path.exists():
                return bin_path
    raise FileNotFoundError('Venv not found')


def check_pip_exists(project_python: Path) -> bool:
    return (project_python / 'pip').exists()


def get_package_list(project_path: Path) -> list[str]:
    venv_path = get_venv_path(project_path)
    if not check_pip_exists(venv_path):
        raise FileNotFoundError('Pip not found')
    pip_path = str(venv_path / 'pip')
    return subprocess.check_output([pip_path, 'freeze']).decode()


def get_all_packages(project_path: Path) -> list[str]:
    # get the packages list
    try:
        packages = get_package_list(project_path)
    except FileNotFoundError:
        raise FileNotFoundError('Pip not found')
    # parse the packages list
    packages = packages.split('\n')
    # return the packages list
    all_packages = []
    for i in packages:
        if len(i) == 0:
            continue
        if '==' in i:
            name, version = i.split('==')
        elif '>=' in i:
            name, version = i.split('>=')
        else:
            name = i
            version = ''
        all_packages.append(Package(name, version))
    return all_packages
