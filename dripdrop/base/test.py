import asyncio
import shutil
import traceback
from datetime import datetime
from fastapi import status
from httpx import AsyncClient
from pydantic import BaseModel
from typing import TypeVar, AsyncContextManager
from unittest import IsolatedAsyncioTestCase

from dripdrop.app import app
from dripdrop.authentication.app import password_context
from dripdrop.authentication.dependencies import COOKIE_NAME
from dripdrop.authentication.models import User
from dripdrop.models import Base
from dripdrop.services import database, http_client, redis_client, s3, temp_files
from dripdrop.settings import settings, ENV

T = TypeVar("T")


class BaseTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.maxDiff = None
        self.assertEqual(settings.env, ENV.TESTING)
        await self.delete_temp_directories()
        await temp_files._create_temp_directory()
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        self.client = await self.enter_async_context(
            AsyncClient(app=app, base_url="http://test")
        )
        self.session = await self.enter_async_context(database.create_session())
        self.http_client = await self.enter_async_context(http_client.create_client())
        self.redis = await self.enter_async_context(redis_client.create_client())
        await self.redis.flushall()

    async def asyncTearDown(self):
        await self.delete_temp_directories()

    async def enter_async_context(self, context_manager: AsyncContextManager[T]) -> T:
        self.addAsyncCleanup(context_manager.__aexit__, None, None, None)
        return await context_manager.__aenter__()

    async def delete_temp_directories(self):
        try:
            await asyncio.to_thread(shutil.rmtree, temp_files.TEMP_DIRECTORY)
        except Exception:
            pass

    async def clean_test_s3_folders(self):
        try:
            async for keys in s3.list_objects():
                for key in keys:
                    if key.startswith("assets/"):
                        continue
                    await s3.delete_file(filename=key)
        except Exception:
            print(traceback.format_exc())

    async def create_user(self, email: str, password: str, admin=False, verified=True):
        user = User(
            email=email,
            password=password_context.hash(password),
            admin=admin,
            verified=verified,
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def create_and_login_user(self, email: str, password: str, admin=False):
        user = await self.create_user(email=email, password=password, admin=admin)
        response = await self.client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get(COOKIE_NAME))
        return user

    def convert_to_time_string(self, dt: datetime):
        class DatetimeModel(BaseModel):
            dt: datetime

        return DatetimeModel(dt=dt).model_dump(mode="json")["dt"]
