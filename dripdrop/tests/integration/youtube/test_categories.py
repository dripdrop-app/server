from fastapi import status
from httpx import AsyncClient

CATEGORIES_URL = "/api/youtube/videos/categories"


async def test_get_categories_when_not_logged_in(client: AsyncClient):
    response = await client.get(CATEGORIES_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_categories_with_no_categories(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(CATEGORIES_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"categories": []}


async def test_get_categories_with_no_videos(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_video_category(id=1, name="category")
    response = await client.get(CATEGORIES_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"categories": []}


async def test_get_categories_with_subscribed_channels(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_subscription,
    create_video,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(channel_id=channel.id, email=user.email)
    category = await create_video_category(id=1, name="category")
    await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.get(CATEGORIES_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "categories": [{"id": category.id, "name": category.name}]
    }


async def test_get_categories_with_specific_channel(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.get(CATEGORIES_URL, params={"channel_id": channel.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "categories": [{"id": category.id, "name": category.name}]
    }


async def test_get_categories_with_distinct_results(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.get(CATEGORIES_URL, params={"channel_id": channel.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "categories": [{"id": category.id, "name": category.name}]
    }


async def test_get_categories_with_multiple_results_in_ascending_name_order(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    categories = [
        await create_video_category(id=i, name=f"category_{i}") for i in range(5)
    ]
    for i in range(5):
        await create_video(
            id=str(i),
            title=f"title_{i}",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=categories[i].id,
        )
    response = await client.get(CATEGORIES_URL, params={"channel_id": channel.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "categories": list(
            map(lambda category: {"id": category.id, "name": category.name}, categories)
        )
    }
