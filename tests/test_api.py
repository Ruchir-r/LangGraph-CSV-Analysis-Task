"""
API integration tests for the LangGraph CSV Analysis platform.
"""

import pytest
import json
import io
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


class TestHealthAPI:
    """Test health check endpoints."""
    
    def test_health_check(self, test_client):
        """Test basic health check endpoint."""
        response = test_client.get("/api/v2/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    def test_health_check_with_database(self, test_client, mock_database):
        """Test health check with database connection."""
        response = test_client.get("/api/v2/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"


class TestFileUploadAPI:
    """Test file upload endpoints."""
    
    def test_upload_csv_file(self, test_client, sample_csv_data):
        """Test uploading a CSV file."""
        # Create CSV content
        csv_content = sample_csv_data.to_csv(index=False)
        
        # Mock file upload
        files = {"files": ("test.csv", io.StringIO(csv_content), "text/csv")}
        
        with patch('app.file_routes.save_uploaded_file') as mock_save:
            mock_save.return_value = {"id": "test-file-123", "filename": "test.csv"}
            
            response = test_client.post("/api/v2/files/upload", files=files)
            assert response.status_code == 200
            
            data = response.json()
            assert "files" in data
            assert len(data["files"]) > 0
    
    def test_list_files(self, test_client, mock_database):
        """Test listing uploaded files."""
        response = test_client.get("/api/v2/files/")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert isinstance(data["files"], list)
    
    def test_upload_invalid_file_type(self, test_client):
        """Test uploading invalid file type."""
        files = {"files": ("test.txt", io.StringIO("invalid content"), "text/plain")}
        
        response = test_client.post("/api/v2/files/upload", files=files)
        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 422]


class TestAnalysisAPI:
    """Test analysis endpoints."""
    
    def test_simple_analysis(self, test_client, mock_workflow):
        """Test simple analysis endpoint."""
        payload = {
            "query": "Show average revenue by region",
            "files": [{"id": "test-file-123", "filename": "test.csv"}]
        }
        
        with patch('app.analysis_routes.get_llm_service') as mock_llm:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "analysis_result": "Average revenue by region: APAC: $1500, EU: $2000, NA: $1800"
            })
            mock_llm.return_value.generate_response.return_value = mock_response
            
            response = test_client.post("/api/v2/analysis/simple", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "result" in data
    
    def test_comprehensive_analysis(self, test_client, mock_workflow):
        """Test comprehensive analysis endpoint."""
        payload = {
            "query": "Analyze revenue trends and provide insights",
            "files": [{"id": "test-file-123", "filename": "test.csv"}],
            "session_id": "test-session-123"
        }
        
        response = test_client.post("/api/v2/analysis/comprehensive", json=payload)
        # Should start the analysis process
        assert response.status_code in [200, 202]
        
        data = response.json()
        assert "execution_id" in data or "result" in data
    
    def test_analysis_with_invalid_query(self, test_client):
        """Test analysis with invalid query."""
        payload = {
            "query": "",  # Empty query
            "files": []   # No files
        }
        
        response = test_client.post("/api/v2/analysis/simple", json=payload)
        assert response.status_code in [400, 422]  # Should return validation error


class TestSessionAPI:
    """Test session management endpoints."""
    
    def test_create_session(self, test_client, mock_database):
        """Test creating a new session."""
        payload = {"user_id": "test-user"}
        
        response = test_client.post("/api/v2/sessions/", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
    
    def test_list_sessions(self, test_client, mock_database):
        """Test listing sessions."""
        response = test_client.get("/api/v2/sessions/")
        assert response.status_code == 200
        
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
    
    def test_get_session_details(self, test_client, mock_database):
        """Test getting session details."""
        session_id = "test-session-123"
        
        response = test_client.get(f"/api/v2/sessions/{session_id}")
        # Should either return session details or 404 if not found
        assert response.status_code in [200, 404]


class TestWebSocketAPI:
    """Test WebSocket functionality."""
    
    def test_websocket_connection(self, test_client):
        """Test WebSocket connection establishment."""
        session_id = "test-session-123"
        
        with test_client.websocket_connect(f"/api/v2/ws/{session_id}") as websocket:
            # Connection should be established successfully
            assert websocket is not None
    
    @patch('app.websocket_routes.register_progress_callback')
    def test_websocket_progress_updates(self, mock_register, test_client):
        """Test receiving progress updates via WebSocket."""
        session_id = "test-session-123"
        
        with test_client.websocket_connect(f"/api/v2/ws/{session_id}") as websocket:
            # Simulate receiving a progress update
            test_message = {
                "type": "progress_update",
                "execution_id": "test-exec-123",
                "progress_percentage": 50.0,
                "status_message": "Processing data..."
            }
            
            # In a real test, you'd send this from the server
            # For now, just verify the connection works
            assert websocket is not None


class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_endpoint(self, test_client):
        """Test non-existent endpoint returns 404."""
        response = test_client.get("/api/v2/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, test_client):
        """Test wrong HTTP method returns 405."""
        response = test_client.delete("/api/v2/health")
        assert response.status_code == 405
    
    def test_invalid_json_payload(self, test_client):
        """Test invalid JSON payload handling."""
        response = test_client.post(
            "/api/v2/analysis/simple",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestAuthentication:
    """Test authentication and security."""
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are present."""
        response = test_client.get("/api/v2/health")
        assert response.status_code == 200
        
        # Check for CORS headers (if implemented)
        headers = response.headers
        # This depends on your CORS setup
    
    def test_rate_limiting(self, test_client):
        """Test rate limiting (if implemented)."""
        # Make multiple rapid requests
        responses = []
        for _ in range(5):
            response = test_client.get("/api/v2/health")
            responses.append(response.status_code)
        
        # All should succeed unless rate limiting is very strict
        assert all(status == 200 for status in responses[:3])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])