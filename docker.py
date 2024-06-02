import argparse
import dotenv
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
        env: str = ...,
        project: str = "dripdrop",
    ):
        self._compose_file = compose_file
        self._env = env
        self._project = project
        self._image_tag = f"{self._project}/image"
        self._env_vars = {
            **dotenv.dotenv_values(".env"),
            "ENV": self._env,
            "IMAGE": self._image_tag,
        }

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
            env=self._env_vars,
        ).check_returncode()

    def _build_services(self):
        subprocess.run(
            [
                "docker",
                "image",
                "build",
                "-f",
                "Dockerfile",
                "-t",
                self._image_tag,
                ".",
            ],
        ).check_returncode()
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
            env=self._env_vars,
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
            env=self._env_vars,
        ).check_returncode()

    def deploy(self):
        if self._env == DEVELOPMENT:
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
                "dripdrop-server",
                "poetry",
                "run",
                "python",
                "-m",
                "unittest",
                "discover",
            ],
            env=self._env_vars,
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

    compose_file = (
        "docker-compose.prod.yml"
        if args.action == DEPLOY and args.env == PRODUCTION
        else "docker-compose.yml"
    )

    docker_interface = DockerInterface(
        compose_file=compose_file, env=TESTING if args.action == TEST else args.env
    )

    if args.action == REMOVE:
        docker_interface.remove_services()
    elif args.action == DEPLOY:
        docker_interface.deploy()
    elif args.action == TEST:
        docker_interface.test()
