"""
This file contains the tests for the app.py file.
"""

# pylint: disable=redefined-outer-name

import os
import time
from datetime import datetime, timedelta, timezone
from multiprocessing import Value
from typing import Generator, List, Tuple

import pytest
from flask.testing import FlaskClient

import database as db
from app import App
from model import Model, ModelMocked

# Shared counter for port numbers
port_counter = Value("i", 5000)


@pytest.fixture
def app(monkeypatch) -> Generator[Tuple[App, int], None, None]:
    """
    Create an App object for testing and teardown after testing.
    """
    test_name = os.environ.get("PYTEST_CURRENT_TEST")
    if test_name is None:
        test_name = "unknown"
    else:
        test_name = test_name.split(":")[-1].split(" ")[0]
    db_path = f"test_database_{test_name}.db"
    monkeypatch.setattr("database.main.DB_PATH", db_path)
    with port_counter.get_lock():
        port = port_counter.value
        port_counter.value += 1
    model = Model(ModelMocked("short"))
    app = App(model=model, port=port)
    yield app
    os.remove(db_path)


@pytest.fixture
def client(app: App) -> Generator[FlaskClient, None, None]:
    """
    Create a Flask test client for testing and teardown after testing.
    """
    with app.app.test_client() as client:
        yield client


@pytest.fixture
def chars(app: App) -> Generator[List[db.Character], None, None]:
    """
    Create characters for tests.
    """
    char_1 = db.Character(name="test")
    char_id_1 = db.insert_character(char_1)
    character_1 = db.select_character(char_id_1)
    char_2 = db.Character(name="test2")
    char_id_2 = db.insert_character(char_2)
    character_2 = db.select_character(char_id_2)
    yield [character_1, character_2]


@pytest.fixture
def threads(chars: List[db.Character]) -> Generator[List[db.Thread], None, None]:
    """
    Create threads for tests.
    """
    thread_id_1 = db.insert_thread("user", chars[0]["id"])
    thread_1 = db.select_thread(thread_id_1)
    thread_id_2 = db.insert_thread("user", chars[1]["id"])
    thread_2 = db.select_thread(thread_id_2)
    yield [thread_1, thread_2]


@pytest.fixture
def messages(threads: List[db.Thread]) -> Generator[List[db.Message], None, None]:
    """
    Create messages for tests.
    """
    m_1 = db.Message(thread=threads[0], content="content1", role="user")
    message_id_1 = db.insert_message(m_1)
    message_1 = db.select_message(message_id_1)
    time.sleep(1)
    m_2 = db.Message(thread=threads[0], content="content2", role="assistant")
    message_id_2 = db.insert_message(m_2)
    message_2 = db.select_message(message_id_2)
    m_3 = db.Message(thread=threads[1], content="content3", role="user")
    message_id_3 = db.insert_message(m_3)
    message_3 = db.select_message(message_id_3)
    yield [message_1, message_2, message_3]


@pytest.fixture
def events(chars: List[db.Character]) -> Generator[List[db.Event], None, None]:
    """
    Create events for tests.
    """
    e_1 = db.Event(
        character=chars[0]["id"],
        type="event",
        content="event 1",
    )
    e_1["id"] = db.insert_event(e_1)
    e_2 = db.Event(
        character=chars[0]["id"],
        type="thought",
        content="thought 1",
    )
    e_2["id"] = db.insert_event(e_2)
    e_3 = db.Event(
        character=chars[1]["id"],
        type="event",
        content="event 2",
    )
    e_3["id"] = db.insert_event(e_3)
    yield [e_1, e_2, e_3]


@pytest.fixture
def posts(chars: List[db.Character]) -> Generator[List[db.Post], None, None]:
    """
    Create posts for tests.
    """
    p_1 = db.Post(
        character=chars[0]["id"],
        description="test post",
        prompt="test prompt",
        caption="test caption",
        image_path="test image path",
    )
    p_1["id"] = db.insert_social_media_post(p_1)
    p_2 = db.Post(
        character=chars[0]["id"],
        description="test post2",
        prompt="test prompt2",
        caption="test caption2",
        image_path="test image path2",
    )
    p_2["id"] = db.insert_social_media_post(p_2)
    yield [p_1, p_2]


def test_ready(client: FlaskClient) -> None:
    """
    Test the readiness route.
    """
    response = client.get("/readiness")
    assert response.status_code == 200


def test_new_thread(client: FlaskClient, chars: List[db.Character]) -> None:
    """
    Test the new thread route.
    """
    response = client.post(
        "/threads/new",
        json={"username": "user", "character": chars[0]["id"]},
    )
    assert response.status_code == 200
    assert response.data == b"1"


def test_get_threads_by_user(threads: List[db.Thread], client: FlaskClient) -> None:
    """
    Test the get threads by user route.
    """
    response = client.get("/threads/user")
    assert response.status_code == 200
    assert response.json[0]["id"] == threads[0]["id"]
    assert response.json[1]["id"] == threads[1]["id"]


def test_get_messages_by_thread(
    threads: List[db.Thread],
    messages: List[db.Message],
    client: FlaskClient,
) -> None:
    """
    Test the get messages by thread route.
    """
    response = client.get(f"/threads/{threads[0]['id']}/messages")
    assert response.json
    assert response.json[0]["id"] == messages[0]["id"]
    assert response.json[1]["id"] == messages[1]["id"]
    assert response.status_code == 200


def test_delete_messages_more_recent(
    messages: List[db.Message], client: FlaskClient
) -> None:
    """
    Test the delete messages more recent route.
    """
    response = client.delete(f"/messages/{messages[0]['id']}")
    assert response.status_code == 200
    with pytest.raises(ValueError):
        db.select_message(messages[1]["id"])


def test_get_response_now(threads: List[db.Thread], client: FlaskClient) -> None:
    """
    Test the get response now route.
    """
    # Check that the response is applied
    response = client.get(f"/threads/{threads[0]['id']}/messages/new")
    assert response.status_code == 200
    time.sleep(1)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert messages[-1]["timestamp"] < datetime.now(timezone.utc)


def test_get_response_now_new(
    threads: List[db.Thread], messages: List[db.Message], client: FlaskClient
) -> None:
    """
    Test the get response now route.
    """
    time.sleep(2)

    # Check that a new response is generated if there is no scheduled message
    response = client.get(f"/threads/{threads[0]['id']}/messages/new")
    assert response.status_code == 200
    time.sleep(2)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 3
    assert messages[-1]["content"] == "Mock response"
    assert messages[-1]["timestamp"] < datetime.now(timezone.utc)


def test_get_events_by_character(events: List[db.Event], client: FlaskClient) -> None:
    """
    Test the get events by character route.
    """
    response = client.get(f"/events/{events[0]['character']}")
    assert response.status_code == 200
    assert response.json[0]["id"] == events[0]["id"]
    assert response.json[1]["id"] == events[1]["id"]


def test_get_posts_by_character(posts: List[db.Post], client: FlaskClient) -> None:
    """
    Test the get posts by character route.
    """

    response = client.get(f"/posts/{posts[0]['character']}")
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["description"] == posts[0]["description"]
    assert response.json[1]["description"] == posts[1]["description"]
