from dripdrop.authentication.models import User
from dripdrop.music.models import MusicJobs
from dripdrop.youtube.models import (
    GoogleAccounts,
    YoutubeChannels,
    YoutubeSubscriptions,
    YoutubeVideoCategories,
    YoutubeVideoLikes,
    YoutubeVideoQueues,
    YoutubeVideos,
    YoutubeVideoWatches,
)
from sqlalchemy import MetaData

metadata = MetaData()

User.metadata = metadata
MusicJobs.metadata = metadata
GoogleAccounts.metadata = metadata
YoutubeChannels.metadata = metadata
YoutubeVideoCategories.metadata = metadata
YoutubeSubscriptions.metadata = metadata
YoutubeVideos.metadata = metadata
YoutubeVideoLikes.metadata = metadata
YoutubeVideoQueues.metadata = metadata
YoutubeVideoWatches.metadata = metadata
