import os

from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "../templates")),
    enable_async=True,
)
