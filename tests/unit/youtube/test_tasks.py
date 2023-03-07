from pytest import MonkeyPatch
from sqlalchemy import select

from dripdrop.apps.youtube.models import YoutubeVideoCategory
from dripdrop.apps.youtube.tasks import youtube_tasker
from dripdrop.database import AsyncSession


async def test_update_video_categories_with_failed_google_api_request(
    monkeypatch: MonkeyPatch, session: AsyncSession
):
    def raise_exception():
        raise Exception("Fail")

    monkeypatch.setattr(
        "dripdrop.services.google_api.google_api.get_video_categories", raise_exception
    )
    await youtube_tasker.update_video_categories(cron=True, session=session)
    query = select(YoutubeVideoCategory)
    results = await session.scalars(query)
    assert len(results.all()) == 0


async def test_update_video_categories_with_no_categories(
    monkeypatch: MonkeyPatch, session: AsyncSession
):
    async def mock_video_categories():
        return []

    monkeypatch.setattr(
        "dripdrop.services.google_api.google_api.get_video_categories",
        mock_video_categories,
    )
    await youtube_tasker.update_video_categories(cron=True, session=session)
    query = select(YoutubeVideoCategory)
    results = await session.scalars(query)
    assert len(results.all()) == 0


async def test_update_video_categories_with_categories(
    monkeypatch: MonkeyPatch, session: AsyncSession
):
    categories = [{"id": i, "snippet": {"title": f"category{i}"}} for i in range(5)]

    async def mock_video_categories():
        return categories

    monkeypatch.setattr(
        "dripdrop.services.google_api.google_api.get_video_categories",
        mock_video_categories,
    )
    await youtube_tasker.update_video_categories(cron=True, session=session)
    query = select(YoutubeVideoCategory)
    results = await session.scalars(query)
    assert len(results.all()) == 5
