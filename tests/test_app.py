import sys
import os
from pathlib import Path

# Ensure `src` is on sys.path so we can import `app` directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_root_redirect_ArrangeActAssert():
    # Arrange: nothing to set up
    # Act
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code in (307, 302)
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities_ArrangeActAssert():
    # Arrange
    expected = set(activities.keys())
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == expected


def test_signup_for_activity_success_ArrangeActAssert():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@example.com"
    original_participants = list(activities[activity]["participants"])
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    # Cleanup
    activities[activity]["participants"] = original_participants


def test_signup_for_activity_already_signed_ArrangeActAssert():
    # Arrange
    activity = "Chess Club"
    email = "already@mergington.edu"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)
    original_participants = list(activities[activity]["participants"])
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    # Cleanup
    activities[activity]["participants"] = original_participants


def test_unregister_for_activity_success_ArrangeActAssert():
    # Arrange
    activity = "Programming Class"
    email = "temp@student.edu"
    original_participants = list(activities[activity]["participants"])
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)
    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert response.json()["message"] == f"Removed {email} from {activity}"
    # Cleanup
    activities[activity]["participants"] = original_participants


def test_unregister_not_signed_ArrangeActAssert():
    # Arrange
    activity = "Programming Class"
    email = "notthere@student.edu"
    original_participants = list(activities[activity]["participants"])
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 404
    # Cleanup
    activities[activity]["participants"] = original_participants
