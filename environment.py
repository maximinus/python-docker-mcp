import os
import shutil
import docker
import tempfile
import subprocess

from pathlib import Path
from dataclasses import dataclass

client = docker.from_env()

volumes = {
    "/path/to/temp/project": {"bind": "/app", "mode": "rw"},
    "/home/username/.cache/uv": {"bind": "/root/.cache/uv", "mode": "rw"},
}


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

class SandboxManager:
    def __init__(self, project_root: str, python_version: str = "3.11"):
        self.project_root = os.path.abspath(project_root)
        self.python_version = python_version
        self.docker_client = docker.from_env()
        self.temp_dir = tempfile.mkdtemp()
        self.volume_name = None
        self.image_tag = f"python:{self.python_version}-slim"

        self._prepare_environment()

    def _prepare_environment(self):
        self._pull_python_image()
        self._copy_project()

    def _pull_python_image(self):
        try:
            self.docker_client.images.get(self.image_tag)
        except docker.errors.ImageNotFound:
            print(f'Pulling Docker image {self.image_tag}...')
            self.docker_client.images.pull(self.image_tag)

    def _copy_project(self):
        def ignore_unwanted_files(dir, files):
            ignore_list = []
            for f in files:
                if f in ("venv", ".venv",".git", "__pycache__"):
                    ignore_list.append(f)
            return ignore_list

        shutil.copytree(
            self.project_root, 
            self.temp_dir, 
            ignore=ignore_unwanted_files, 
            dirs_exist_ok=True
        )

    def _generate_uv_install_command(self, packages: List[Package]) -> str:
        if not packages:
            return "echo 'No packages to install'"
        parts = [f'{pkg.name}=={pkg.version}' for pkg in packages]
        return f'uv pip install {" ".join(parts)}'

    def run(self, command: str, timeout_seconds: int = 10) -> str:
        uv_cache_host = os.path.expanduser("~/.cache/uv")
        volumes = {
            self.temp_dir: {"bind": "/app", "mode": "rw"},
            uv_cache_host: {"bind": "/root/.cache/uv", "mode": "rw"},
        }

        try:
            packages = get_all_packages(self.project_root)
        except FileNotFoundError:
            packages = []

        uv_install_command = self._generate_uv_install_command(packages)

        full_command = f"{uv_install_command} && timeout {timeout_seconds}s {command}"

        container = self.docker_client.containers.run(
            image=self.image_tag,
            command=['bash', '-c', full_command],
            volumes=volumes,
            working_dir='/app',
            network_mode='bridge',
            mem_limit='512m',
            cpus=0.5,
            remove=True,
            detach=True
        )

        output = container.logs(stdout=True, stderr=True).decode('utf-8')
        return f'{output.strip()}'

    def cleanup(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp dir: {e}")


if __name__ == "__main__":
    example_project = Path(__file__).parent / 'test_project'
    sandbox = SandboxManager(example_project, python_version='3.10.12')
    output = sandbox.run('python example.py')
    print(output)
    sandbox.cleanup()
