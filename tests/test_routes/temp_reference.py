def test_get_messages_by_thread(
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
    assert messages[1]["id"]
    response = client.delete(f"/messages/{messages[0]['id']}")
    assert response.status_code == 200
    with pytest.raises(ValueError):
        db.select_message(messages[1]["id"])


def test_get_response_now(threads: List[db.Thread], client: FlaskClient) -> None:
    """
    Test the get response now route.
    """
    assert threads[0]["id"]
    # Check that the response is applied
    response = client.get(f"/threads/{threads[0]['id']}/messages/new")
    assert response.status_code == 200
    time.sleep(1)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert messages[-1]["timestamp"]
    assert messages[-1]["timestamp"] < datetime.now(timezone.utc)


def test_get_response_now_new(
    threads: List[db.Thread], messages: List[db.Message], client: FlaskClient
) -> None:
    """
    Test the get response now route.
    """
    assert threads[0]["id"]
    time.sleep(2)

    # Check that a new response is generated if there is no scheduled message
    response = client.get(f"/threads/{threads[0]['id']}/messages/new")
    assert response.status_code == 200
    time.sleep(2)
    messages = db.select_messages_by_thread(threads[0]["id"])
    assert len(messages) == 3
    assert messages[-1]["content"] == "Mock response"
    assert messages[-1]["timestamp"]
    assert messages[-1]["timestamp"] < datetime.now(timezone.utc)
