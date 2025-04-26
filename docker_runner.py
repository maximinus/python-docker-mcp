import docker
import os

client = docker.from_env()

def run_in_docker(command: str, image: str = "python:3.11-slim") -> str:
    try:
        container = client.containers.run(
            image=image,
            command=["bash", "-c", f"timeout 10s {command}"],
            volumes={
                os.getcwd(): {
                    'bind': '/app',
                    'mode': 'ro'  # or 'rw' if needed
                }
            },
            working_dir="/app",
            network_mode="none",
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,  # 0.5 CPU
            remove=True,
            stderr=True,
            stdout=True,
            detach=True
        )
        output = container.logs(stdout=True, stderr=True).decode("utf-8")
        exit_code = container.wait()["StatusCode"]
        return f"Exit Code: {exit_code}\n\nOUTPUT:\n{output.strip()}"
    except docker.errors.ContainerError as e:
        return f"Container error: {e}"
    except docker.errors.ImageNotFound:
        return "Docker image not found. Pulling may be required."
    except Exception as e:
        return f"Error: {str(e)}"
