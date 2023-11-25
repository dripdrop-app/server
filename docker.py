import argparse
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
        self._env_vars = None

    def _load_environment_variables(self):
        if self._env_vars is None:
            self._env_vars = {"ENV": self._env, "IMAGE": self._image_tag}
            lines = []
            with open(".env") as f:
                lines = f.readlines()
            for line in lines:
                variable, value = line.split("=")
                self._env_vars[variable] = value.strip()
        return self._env_vars

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
            env=self._load_environment_variables(),
        ).check_returncode()

    def _build_services(self, no_cache=False):
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
        if no_cache:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "--no-cache",
                    "-p",
                    self._project,
                    "-f",
                    self._compose_file,
                    "build",
                ],
                env=self._load_environment_variables(),
            ).check_returncode()
        else:
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
            env=self._load_environment_variables(),
        ).check_returncode()

    def deploy(self):
        if self._env == DEVELOPMENT:
            self.remove_services()
        self._build_services()
        self._deploy_services()

    def test(self):
        self._build_services(no_cache=True)
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
