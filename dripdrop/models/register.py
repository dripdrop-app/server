from dripdrop.apps.authentication.models import User
from dripdrop.apps.music.models import MusicJob
from dripdrop.apps.youtube.models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideo,
    YoutubeVideoWatch,
)

from .base import Base


class Register:
    def __init__(self):
        self.models = [
            User,
            MusicJob,
            GoogleAccount,
            YoutubeChannel,
            YoutubeSubscription,
            YoutubeVideoCategory,
            YoutubeVideoLike,
            YoutubeVideoQueue,
            YoutubeVideo,
            YoutubeVideoWatch,
        ]
        self.base = Base


register = Register()
