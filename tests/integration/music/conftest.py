import pytest

from ...conftest import TEST_EMAIL, TEST_PASSWORD


@pytest.fixture(autouse=True)
def create_default_user(create_and_login_user):
    create_and_login_user(email=TEST_EMAIL, password=TEST_PASSWORD, admin=False)
