import argparse
import os
import subprocess
import time


def build_docker_image(tag: str = ..., docker_file: str = ..., context: str = ...):
    subprocess.run(["docker", "image", "rm", tag, "--force"])
    subprocess.run(
        ["docker", "image", "build", "--tag", tag, "-f", docker_file, context]
    ).check_returncode()


def remove_stack(stack: str = ...):
    subprocess.run(["docker", "stack", "rm", stack]).check_returncode()
    while True:
        process = subprocess.run(["docker", "stack", "ps", stack])
        if process.returncode != 0:
            break
        time.sleep(1)


def load_environment_variables(env_file=...):
    environment = {}
    lines = []
    with open(env_file) as f:
        lines = f.readlines()
    for line in lines:
        variable, value = line.split("=")
        environment[variable] = value.strip()
    return environment


def deploy_stack(stack: str = ..., compose_file: str = ..., env_file: str = ...):
    process = subprocess.run(
        ["docker", "stack", "deploy", "--compose-file", compose_file, "--prune", stack],
        env=load_environment_variables(env_file=env_file),
    )
    process.check_returncode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env", type=str, required=True, choices=["development", "production"]
    )

    args = parser.parse_args()

    current_path = os.path.dirname(os.path.abspath(__file__))
    context = os.path.join(current_path, ".")
    stack = "dripdrop" if args.env == "production" else "dripdrop-dev"
    docker_file = os.path.join(
        current_path,
        "./dockerfiles/Dockerfile.dev"
        if args.env == "development"
        else "./dockerfiles/Dockerfile",
    )
    compose_file = os.path.join(
        current_path,
        "docker-compose.dev.yml"
        if args.env == "development"
        else "docker-compose.prod.yml",
    )
    env_file = os.path.join(current_path, ".env")

    build_docker_image(
        tag=stack,
        docker_file=docker_file,
        context=context,
    )
    if args.env == "development":
        remove_stack(stack=stack)
    deploy_stack(stack=stack, compose_file=compose_file, env_file=env_file)
