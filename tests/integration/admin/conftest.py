import pytest


@pytest.fixture
def create_and_login_default_admin_user(
    create_and_login_user, test_email, test_password
):
    create_and_login_user(email=test_email, password=test_password, admin=True)
