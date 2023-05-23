import argparse
import os
import subprocess

DEVELOPMENT = "development"
PRODUCTION = "production"
TESTING = "testing"

REMOVE = "remove"
DEPLOY = "deploy"
TEST = "test"


class DockerInterface:
    def __init__(
        self,
        compose_file: str = ...,
        env_file: str = ...,
        env: str = ...,
        context: str = ...,
        project: str = ...,
    ) -> None:
        self._docker_file = "./Dockerfile"
        self._compose_file = compose_file
        self._env_file = env_file
        self._env = env
        self._context = context
        self._project = project
        self._image_tag = f"{project}/image"
        self._env_vars = None

    def remove_services(self):
        subprocess.run(
            [
                "docker",
                "compose",
                "-p",
                self._project,
                "-f",
                self._compose_file,
                "down",
            ],
            stdout=subprocess.STDOUT,
            stderr=subprocess.STDOUT,
            env=self._load_environment_variables(),
        ).check_returncode()

    def _load_environment_variables(self):
        if self._env_vars is None:
            self._env_vars = {"ENV": self._env, "IMAGE": self._image_tag}
            lines = []
            with open(self._env_file) as f:
                lines = f.readlines()
            for line in lines:
                variable, value = line.split("=")
                self._env_vars[variable] = value.strip()
        return self._env_vars

    def _build_image(self):
        subprocess.run(
            [
                "docker",
                "image",
                "build",
                "-f",
                self._docker_file,
                "-t",
                self._image_tag,
                self._context,
            ],
            stdout=subprocess.STDOUT,
            stderr=subprocess.STDOUT,
        ).check_returncode()

    def _build_services(self):
        self._build_image()
        subprocess.run(
            [
                "docker",
                "compose",
                "-p",
                self._project,
                "-f",
                self._compose_file,
                "build",
            ],
            stdout=subprocess.STDOUT,
            stderr=subprocess.STDOUT,
            env=self._load_environment_variables(),
        ).check_returncode()

    def _deploy_services(self):
        subprocess.run(
            [
                "docker",
                "compose",
                "-p",
                self._project,
                "-f",
                self._compose_file,
                "up",
                "--remove-orphans",
                "--wait",
            ],
            stdout=subprocess.STDOUT,
            stderr=subprocess.STDOUT,
            env=self._load_environment_variables(),
        ).check_returncode()

    def deploy(self, env: str = ...):
        if env == DEVELOPMENT:
            self.remove_services()
        self._build_services()
        self._deploy_services()

    def test(self):
        self._build_services()
        subprocess.run(
            [
                "docker",
                "compose",
                "-p",
                self._project,
                "-f",
                self._compose_file,
                "run",
                "--rm",
                "server",
                "poetry",
                "run",
                "python",
                "-m",
                "unittest",
                "discover",
            ],
            env=self._load_environment_variables(),
        ).check_returncode()
        self.remove_services()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        required=True,
        choices=[DEVELOPMENT, PRODUCTION],
    )
    parser.add_argument(
        "--action", type=str, required=True, choices=[REMOVE, DEPLOY, TEST]
    )

    args = parser.parse_args()

    current_path = os.path.dirname(os.path.abspath(__file__))
    context = os.path.join(current_path, ".")

    OPTIONS = {
        DEVELOPMENT: {
            "project": "dripdrop-dev",
            "compose_file": os.path.join(current_path, "docker-compose.dev.yml"),
        },
        PRODUCTION: {
            "project": "dripdrop",
            "compose_file": os.path.join(current_path, "docker-compose.prod.yml"),
        },
    }

    env_file = os.path.join(current_path, ".env")
    docker_interface = DockerInterface(
        **OPTIONS[args.env],
        env_file=env_file,
        context=context,
        env=TESTING if args.action == TEST else args.env,
    )

    if args.action == REMOVE:
        docker_interface.remove_services()
    elif args.action == DEPLOY:
        docker_interface.deploy()
    elif args.action == TEST:
        docker_interface.test()
