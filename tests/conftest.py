import pytest
from Myflask import app as flask_app

@pytest.fixture
def client():  # 所有测试文件，都可以直接用 client
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
