import sys
import os
import pytest

# Add the project root to sys.path so Python can find 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client