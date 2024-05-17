import argparse
import dotenv
import subprocess


DEVELOPMENT = "development"
PRODUCTION = "production"
TESTING = "testing"

REMOVE = "remove"
DEPLOY = "deploy"
TEST = "test"


class DockerInterface:
    def __init__(self, compose_file: str = ..., project: str = "dripdrop"):
        self._compose_file = compose_file
        self._env = dotenv.dotenv_values()
        self._project = project
        self._image_tag = f"{self._project}/image"
        self._env_vars = None

    def remove_services(self):
        subprocess.run(
            ["docker", "stack", "rm", self._project], env=self._env
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

    def _deploy_services(self):
        subprocess.run(
            ["docker", "stack", "deploy", "-c", self._compose_file, self._project],
            env=self._env,
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
            env=self._env,
        ).check_returncode()


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
        "docker-compose.dev.yml"
        if args.env == DEVELOPMENT
        else "docker-compose.prod.yml"
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
