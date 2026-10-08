"""
Unit tests for health check endpoints.

These tests verify:
1. /health endpoint (liveness probe) - is the app running?
2. /ready endpoint (readiness probe) - is the app ready to serve requests?

The /ready endpoint checks if the database is accessible.
We test both success (ready) and failure (not ready) cases.
"""

from unittest.mock import patch


class TestHealthChecks:
    """Test suite for health check endpoints"""

    # ========== LIVENESS CHECK (/health) ==========

    def test_health_check(self, client):
        """
        Test that /health always returns 200 OK.

        This is a liveness probe - it only checks if the app is running,
        not whether it's ready to serve requests.

        Kubernetes uses this to know: "Is the pod alive?"
        If this fails, Kubernetes restarts the container.
        """
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json["status"] == "ok"

    # ========== READINESS CHECK (/ready) - SUCCESS CASE ==========

    def test_ready_check(self, client):
        """
        Test that /ready returns 200 OK when database is accessible.

        This is a readiness probe - it checks if the app is ready
        to accept traffic from load balancer.

        Kubernetes uses this to know: "Can I send requests to this pod?"
        If this fails, Kubernetes removes pod from load balancer
        but keeps the pod running (doesn't restart).
        """
        response = client.get("/ready")

        assert response.status_code == 200
        assert response.json["status"] == "ready"

    # ========== READINESS CHECK (/ready) - FAILURE CASE ==========

    def test_ready_check_fails(self, client, app):
        """
        Test that /ready returns 503 Service Unavailable when DB is not accessible.

        This simulates a database connection failure.
        """

        # Mock the database to fail
        with patch("app.db.session.execute") as mock_execute:
            mock_execute.side_effect = Exception("Database connection failed")

            # Make the request
            response = client.get("/ready")

            assert response.status_code == 503
            assert response.json["status"] == "not ready"
            assert "Database connection failed" in response.json["error"]

            # Verify the database check was actually called
            mock_execute.assert_called_once()
