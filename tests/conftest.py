"""
Test configuration and fixtures for the LangGraph CSV Analysis platform.
"""

import os
import sys
import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Import test fixtures and utilities
from app.database import get_db, FileModel, SessionModel
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    return pd.DataFrame({
        'Order_ID': ['ORD001', 'ORD002', 'ORD003'],
        'Customer_ID': ['CUST001', 'CUST002', 'CUST003'],
        'Region': ['APAC', 'EU', 'NA'],
        'Product': ['Widget-A', 'Widget-B', 'Widget-C'],
        'Revenue': [1000.50, 2500.75, 1800.25],
        'Units': [10, 25, 18],
        'Discount': [0.1, 0.15, 0.05],
        'Meta.channel': ['online', 'retail', 'partner'],
        'Date': ['2024-11-01', '2024-11-02', '2024-11-03']
    })


@pytest.fixture
def sample_csv_file(sample_csv_data, tmp_path):
    """Create a temporary CSV file with sample data."""
    csv_file = tmp_path / "test_data.csv"
    sample_csv_data.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('services.llm_service.openai.OpenAI') as mock:
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Sample LLM response"
        mock_instance.chat.completions.create.return_value = mock_response
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('app.database.get_db') as mock_db:
        mock_session = Mock()
        mock_db.return_value = mock_session
        yield mock_session


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    test_env = {
        'TESTING': 'true',
        'DATABASE_URL': 'sqlite:///test_db.sqlite',
        'OPENAI_API_KEY': 'test-key-123',
        'LOG_LEVEL': 'WARNING'
    }
    
    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_workflow():
    """Mock LangGraph workflow for testing."""
    with patch('langgraph_workflow.create_workflow_graph') as mock:
        mock_workflow = Mock()
        async def mock_astream(initial_state, config=None):
            # Simulate workflow steps
            steps = [
                {'current_node': 'parse_files', 'completed_nodes': ['parse_files']},
                {'current_node': 'plan_operations', 'completed_nodes': ['parse_files', 'plan_operations']},
                {'current_node': 'execute_code', 'completed_nodes': ['parse_files', 'plan_operations', 'execute_code']},
            ]
            for step in steps:
                yield {**initial_state, **step}
        
        mock_workflow.astream = mock_astream
        mock.return_value.compile.return_value = mock_workflow
        yield mock_workflow


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def create_multi_month_data():
        """Create multi-month sales data for temporal analysis testing."""
        months = ['2024-10', '2024-11', '2024-12']
        regions = ['APAC', 'EU', 'NA']
        products = ['Widget-A', 'Widget-B', 'Widget-C']
        
        data = []
        for month in months:
            for i, region in enumerate(regions):
                for j, product in enumerate(products):
                    data.append({
                        'Order_ID': f'ORD{month.replace("-", "")}{i}{j}',
                        'Customer_ID': f'CUST{i}{j}',
                        'Region': region,
                        'Product': product,
                        'Revenue': 1000 + (i * 100) + (j * 50),
                        'Units': 10 + i + j,
                        'Discount': 0.05 + (i * 0.05),
                        'Meta.channel': ['online', 'retail', 'partner'][j],
                        'Date': f'{month}-01'
                    })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_anomaly_data():
        """Create data with intentional anomalies for testing."""
        data = TestDataGenerator.create_multi_month_data()
        # Add anomalous values
        data.loc[5, 'Revenue'] = 50000  # Unusually high revenue
        data.loc[10, 'Units'] = 1000    # Unusually high units
        return data


# Export test utilities
__all__ = [
    'test_client',
    'sample_csv_data',
    'sample_csv_file',
    'mock_openai_client',
    'mock_database',
    'mock_workflow',
    'TestDataGenerator'
]