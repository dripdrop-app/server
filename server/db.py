import databases
import sqlalchemy
from sqlalchemy.sql.expression import text
from server.config import DATABASE_URL

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("email", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("admin", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("approved", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()")),
)

sessions = sqlalchemy.Table(
    'sessions',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_email", sqlalchemy.ForeignKey(
        users.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_default=text("NOW()"))
)

music_jobs = sqlalchemy.Table(
    'music_jobs',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_email", sqlalchemy.ForeignKey(
        users.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("filename", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("youtube_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("artwork_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("artist", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("album", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("grouping", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("failed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_default=text("NOW()"))
)

google_accounts = sqlalchemy.Table(
    'google_accounts',
    metadata,
    sqlalchemy.Column("email", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_email", sqlalchemy.ForeignKey(
        users.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("access_token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("refresh_token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("expires", sqlalchemy.Numeric, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()")),
    sqlalchemy.Column(
        "last_updated", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()"), server_onupdate=text("NOW()"))
)

youtube_jobs = sqlalchemy.Table(
    'youtube_jobs',
    metadata,
    sqlalchemy.Column("job_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.ForeignKey(
        google_accounts.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("failed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()"))
)

youtube_channels = sqlalchemy.Table(
    'youtube_channels',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("thumbnail", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("upload_playlist_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_default=text("NOW()")),
    sqlalchemy.Column("last_updated", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_onupdate=text("NOW()"))
)

youtube_subscriptions = sqlalchemy.Table(
    'youtube_subscriptions',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('channel_id', sqlalchemy.ForeignKey(
        youtube_channels.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column('email', sqlalchemy.ForeignKey(
        google_accounts.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column(
        'created_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text('NOW()')),
)

youtube_video_categories = sqlalchemy.Table(
    'youtube_video_categories',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Numeric, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        'created_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text('NOW()')),
)

youtube_videos = sqlalchemy.Table(
    'youtube_videos',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('thumbnail', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('channel_id', sqlalchemy.ForeignKey(
        youtube_channels.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column(
        'created_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text('NOW()')),
)

youtube_video_category = sqlalchemy.Table(
    'youtube_video_category',
    metadata,
    sqlalchemy.Column('video_id', sqlalchemy.ForeignKey(
        youtube_videos.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column('category_id', sqlalchemy.ForeignKey(
        youtube_video_categories.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
)
