import importlib

from dripdrop.base.models import Base  # noqa

APPS = [
    "dripdrop.admin",
    "dripdrop.authentication",
    "dripdrop.music",
    "dripdrop.youtube",
]

for app in APPS:
    importlib.import_module(app + ".models")
