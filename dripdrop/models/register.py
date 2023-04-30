import importlib
from dripdrop.models.base import Base  # noqa

APPS = [
    "dripdrop.apps.admin",
    "dripdrop.apps.authentication",
    "dripdrop.apps.music",
    "dripdrop.apps.youtube",
]

for app in APPS:
    importlib.import_module(app + ".models")
