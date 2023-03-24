import pytest
from sqlalchemy import select

from dripdrop.apps.youtube.models import YoutubeVideoCategory
from dripdrop.apps.youtube import tasks as youtube_tasks
from dripdrop.services.database import AsyncSession


@pytest.fixture
def mock_get_video_categories(monkeypatch: pytest.MonkeyPatch):
    def _mock_get_video_categories(func):
        monkeypatch.setattr("dripdrop.services.google_api.get_video_categories", func)

    return _mock_get_video_categories


async def test_update_video_categories_with_failed_google_api_request(
    session: AsyncSession, mock_get_video_categories
):
    def raise_exception():
        raise Exception("Fail")

    mock_get_video_categories(raise_exception)
    with pytest.raises(Exception):
        await youtube_tasks.update_video_categories(cron=True, session=session)
    query = select(YoutubeVideoCategory)
    results = await session.scalars(query)
    assert len(results.all()) == 0


async def test_update_video_categories_with_no_categories(
    session: AsyncSession, mock_get_video_categories
):
    async def mock_video_categories():
        return []

    mock_get_video_categories(mock_video_categories)
    await youtube_tasks.update_video_categories(cron=True, session=session)
    query = select(YoutubeVideoCategory)
    results = await session.scalars(query)
    assert len(results.all()) == 0


async def test_update_video_categories_with_categories(
    session: AsyncSession, mock_get_video_categories
):
    categories = [{"id": i, "snippet": {"title": f"category{i}"}} for i in range(5)]

    async def mock_video_categories():
        return categories

    mock_get_video_categories(mock_video_categories)
    await youtube_tasks.update_video_categories(cron=True, session=session)
    query = select(YoutubeVideoCategory)
    results = await session.scalars(query)
    assert len(results.all()) == 5
