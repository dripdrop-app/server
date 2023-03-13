import argparse
import os
import subprocess

DEVELOPMENT = "development"
PRODUCTION = "production"

REMOVE = "remove"
DEPLOY = "deploy"

class DockerInterface:
    def __init__(self, docker_file: str = ..., compose_file: str = ..., env_file: str = ..., context: str = ..., tag: str = ...) -> None:
        self._REGISTRY_PORT = 5001
        self._REGISTRY_ADDRESS = f"localhost:{self._REGISTRY_PORT}"
        self._docker_file = docker_file
        self._compose_file = compose_file
        self._env_file = env_file
        self._context = context
        self._tag = tag
        self._image = f"{self._REGISTRY_ADDRESS}/{tag}"
        self._env = None

    def _build_docker_image(self):
        subprocess.run(
            [
                "docker",
                "image",
                "build",
                "--tag",
                self._image,
                "-f",
                self._docker_file,
                self._context,
            ]
        ).check_returncode()
        subprocess.run(
            [
                "docker",
                "image",
                "push",
                self._image
            ]
        ).check_returncode()


    def remove_services(self):
        subprocess.run(
            ["docker", "compose", "-p", self._tag, "-f", self._compose_file, "down"], 
            env=self._load_environment_variables()
        ).check_returncode()


    def _load_environment_variables(self):
        if self._env is None:
            self._env = {"IMAGE": self._image}
            lines = []
            with open(self._env_file) as f:
                lines = f.readlines()
            for line in lines:
                variable, value = line.split("=")
                self._env[variable] = value.strip()
        return self._env

    def _deploy_services(self):
        projects = subprocess.run(["docker", "compose", "ls", "--filter", f"name={self._tag}", "--format", "json"], stdout=subprocess.PIPE)
        process = subprocess.run(
            ["docker", "compose", "-p", self._tag, "-f", self._compose_file, "up", "--wait"],
            env=self._load_environment_variables(),
        )
        process.check_returncode()


    def _create_registry(self):
        process = subprocess.run(["docker", "inspect", "registry"])
        if process.returncode != 0:
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "-p",
                    f"{self._REGISTRY_PORT}:5000",
                    "--restart=always",
                    "--mount",
                    "type=volume,src=registry-volume,dst=/var/lib/registry",
                    "--name",
                    "registry",
                    "registry:2",
                ]
            ).check_returncode()

    def deploy(self, env: str = ...):
        self._create_registry()
        self._build_docker_image()
        if env == DEVELOPMENT:
            self.remove_services()
        self._deploy_services()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env", type=str, required=True, choices=[DEVELOPMENT, PRODUCTION],
    )
    parser.add_argument(
        "--action", type=str, required=True, choices=[REMOVE, DEPLOY]
    )

    args = parser.parse_args()

    current_path = os.path.dirname(os.path.abspath(__file__))
    context = os.path.join(current_path, ".")

    development_options = {
        'tag': 'dripdrop-dev',
        'docker_file': os.path.join(current_path, "./dockerfiles/Dockerfile.dev"),
        'compose_file': os.path.join(current_path, "docker-compose.dev.yml"),
    }
    production_options = {
        'tag': 'dripdrop',
        'docker_file': os.path.join(current_path, "./dockerfiles/Dockerfile"),
        'compose_file': os.path.join(current_path, "docker-compose.prod.yml"),     
    }
    options = development_options if args.env == DEVELOPMENT else production_options
    env_file = os.path.join(current_path, ".env")

    docker_interface = DockerInterface(**options, env_file=env_file, context=context)

    if args.action == REMOVE:
        docker_interface.remove_services()
    else:
        docker_interface.deploy()
