"""
Tests for the Mergington High School Activity Management API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save original state
    original_activities = {
        k: {"participants": v["participants"].copy()} 
        for k, v in activities.items()
    }
    
    yield
    
    # Restore original state after test
    for activity_name, activity_data in activities.items():
        activities[activity_name]["participants"] = original_activities[activity_name]["participants"]


class TestGetActivities:
    """Tests for retrieving activities"""
    
    def test_get_activities_returns_list(self, client):
        """Test that GET /activities returns the activities list"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
    def test_get_activities_contains_expected_fields(self, client):
        """Test that activities have expected fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)
            
    def test_get_activities_specific_activity(self, client):
        """Test that specific activities are returned"""
        response = client.get("/activities")
        data = response.json()
        
        # Check for known activities
        assert "Chess Club" in data
        assert "Basketball Team" in data
        assert "Programming Class" in data


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]
        
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        initial_count = len(activities["Soccer Club"]["participants"])
        
        response = client.post(
            "/activities/Soccer Club/signup?email=newstudent@example.com"
        )
        assert response.status_code == 200
        
        assert len(activities["Soccer Club"]["participants"]) == initial_count + 1
        assert "newstudent@example.com" in activities["Soccer Club"]["participants"]
        
    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup?email=duplicate@example.com"
        )
        assert response1.status_code == 200
        
        # Try to signup again with same email
        response2 = client.post(
            "/activities/Chess Club/signup?email=duplicate@example.com"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
        
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@example.com"
        
        response1 = client.post(
            "/activities/Chess Club/signup?email=" + email
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Basketball Team/signup?email=" + email
        )
        assert response2.status_code == 200
        
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Basketball Team"]["participants"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity"""
        email = "unregister@example.com"
        
        # First sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        assert email in activities["Chess Club"]["participants"]
        
        # Then unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        
    def test_unregister_not_registered(self, client):
        """Test unregister when email not in activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
