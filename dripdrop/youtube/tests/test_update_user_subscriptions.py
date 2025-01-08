import asyncio
from unittest.mock import AsyncMock, patch

from sqlalchemy import select

from dripdrop.services import google_api
from dripdrop.youtube.models import YoutubeChannel, YoutubeSubscription
from dripdrop.youtube.tasks import update_user_subscriptions
from dripdrop.youtube.tests.test_base import YoutubeBaseTest


@patch("dripdrop.services.google_api.get_channel_subscriptions")
class TestUpdateUserSubscriptions(YoutubeBaseTest):
    async def test_update_user_subscriptions_with_no_user_channel(
        self, mock_get_channel_subscriptions: AsyncMock
    ):
        user = await self.create_user(email="test@mail.com", password="password")

        await asyncio.to_thread(update_user_subscriptions, email=user.email)

        query = select(YoutubeSubscription).where(
            YoutubeSubscription.email == user.email
        )
        results = await self.session.scalars(query)
        youtube_subscriptions = results.all()
        self.assertEqual(len(youtube_subscriptions), 0)

    async def test_update_user_subscriptions_with_user_channel(
        self, mock_get_channel_subscriptions: AsyncMock
    ):
        user = await self.create_user(email="test@mail.com", password="password")
        test_channel = google_api.YoutubeChannelInfo(
            id="123456", title="title", thumbnail="thumbnail"
        )
        mock_get_channel_subscriptions.return_value = self.create_mock_async_generator(
            [[test_channel]]
        )
        await self.create_user_youtube_channel(email=user.email, channel_id="user_1234")

        await asyncio.to_thread(update_user_subscriptions, email=user.email)

        query = select(YoutubeSubscription).where(
            YoutubeSubscription.email == user.email
        )
        results = await self.session.scalars(query)
        youtube_subscriptions = results.all()
        self.assertEqual(len(youtube_subscriptions), 1)
        youtube_subscription = youtube_subscriptions[0]
        self.assertEqual(youtube_subscription.channel_id, test_channel.id)

        query = select(YoutubeChannel)
        results = await self.session.scalars(query)
        youtube_channels = results.all()
        self.assertEqual(len(youtube_channels), 1)
        youtube_channel = youtube_channels[0]
        self.assertEqual(youtube_channel.id, test_channel.id)
        self.assertEqual(youtube_channel.title, test_channel.title)

    async def test_update_user_subscriptions_with_user_channel_and_existing_subscription(
        self, mock_get_channel_subscriptions: AsyncMock
    ):
        user = await self.create_user(email="test@mail.com", password="password")
        test_channel = google_api.YoutubeChannelInfo(
            id="123456", title="new_title", thumbnail="thumbnailz"
        )
        mock_get_channel_subscriptions.return_value = self.create_mock_async_generator(
            [[test_channel]]
        )
        await self.create_user_youtube_channel(email=user.email, channel_id="user_1234")
        exising_channel = await self.create_youtube_channel(
            id=test_channel.id, title="title", thumbnail=test_channel.thumbnail
        )
        await self.create_youtube_subscription(
            channel_id=exising_channel.id, email=user.email
        )
        # Needed to allow the object to be updated in the task
        self.session.expunge(exising_channel)

        await asyncio.to_thread(update_user_subscriptions, email=user.email)

        query = select(YoutubeSubscription).where(
            YoutubeSubscription.email == user.email
        )
        results = await self.session.scalars(query)
        youtube_subscriptions = results.all()
        self.assertEqual(len(youtube_subscriptions), 1)
        youtube_subscription = youtube_subscriptions[0]
        self.assertEqual(youtube_subscription.channel_id, test_channel.id)

        query = select(YoutubeChannel)
        results = await self.session.scalars(query)
        youtube_channels = results.all()
        self.assertEqual(len(youtube_channels), 1)
        youtube_channel = youtube_channels[0]
        self.assertEqual(youtube_channel.id, test_channel.id)
        self.assertEqual(youtube_channel.title, test_channel.title)

    async def test_update_user_subscriptions_with_user_channel_and_different_subscriptions(
        self, mock_get_channel_subscriptions: AsyncMock
    ):
        user = await self.create_user(email="test@mail.com", password="password")
        test_channel = google_api.YoutubeChannelInfo(
            id="123456", title="new_title", thumbnail="thumbnailz"
        )
        mock_get_channel_subscriptions.return_value = self.create_mock_async_generator(
            [[test_channel]]
        )
        await self.create_user_youtube_channel(email=user.email, channel_id="user_1234")
        exising_channel = await self.create_youtube_channel(
            id="234567", title="title", thumbnail=test_channel.thumbnail
        )
        await self.create_youtube_subscription(
            channel_id=exising_channel.id, email=user.email
        )
        # Needed to allow the object to be updated in the task
        self.session.expunge(exising_channel)

        await asyncio.to_thread(update_user_subscriptions, email=user.email)

        query = select(YoutubeSubscription).where(
            YoutubeSubscription.email == user.email,
            YoutubeSubscription.deleted_at.is_(None),
        )
        results = await self.session.scalars(query)
        youtube_subscriptions = results.all()
        self.assertEqual(len(youtube_subscriptions), 1)
        youtube_subscription = youtube_subscriptions[0]
        self.assertEqual(youtube_subscription.channel_id, test_channel.id)

        # The old channel will still be left in the database even though there
        # are no subscriptions to it
        query = select(YoutubeChannel).order_by(YoutubeChannel.created_at.desc())
        results = await self.session.scalars(query)
        youtube_channels = results.all()
        self.assertEqual(len(youtube_channels), 2)
        youtube_channel = youtube_channels[0]
        self.assertEqual(youtube_channel.title, test_channel.title)
