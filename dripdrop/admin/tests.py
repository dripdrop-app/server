# from dripdrop.settings import settings
# from fastapi.testclient import TestClient
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool


# TEST_DATABASE_URL = settings.test_database_url

# engine = create_async_engine(
#     TEST_DATABASE_URL,
#     poolclass=NullPool,
#     echo=False,
# )
# session_maker = sessionmaker(
#     bind=engine,
#     expire_on_commit=False,
#     class_=AsyncSession,
# )
