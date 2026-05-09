from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_data


@pytest.fixture(autouse=True)
def reset_activities_data():
    original_data = deepcopy(activities_data)
    yield
    activities_data.clear()
    activities_data.update(original_data)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"
    assert data[expected_activity]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_root_redirects_to_static_index_html(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Art Club"
    new_email = "zara@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities_data[activity_name]["participants"]


def test_signup_for_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_email(client):
    # Arrange
    activity_name = "Soccer Club"
    participant_email = "ava@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_activity}/participants", params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}
    assert participant_email not in activities_data[activity_name]["participants"]


def test_remove_participant_nonexistent_returns_404(client):
    # Arrange
    activity_name = "Drama Club"
    missing_email = "nonexistent@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_activity}/participants", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
