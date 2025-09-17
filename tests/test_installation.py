"""
Installation and system tests for the LangGraph CSV Analysis platform.
Tests the basic installation flow and system requirements.
"""

import subprocess
import sys
import os
import time
import requests
import pytest
from pathlib import Path
import tempfile
import shutil


class TestSystemRequirements:
    """Test system requirements and dependencies."""
    
    def test_python_version(self):
        """Test that Python version is 3.8 or higher."""
        major, minor = sys.version_info[:2]
        assert major >= 3, f"Python 3.x required, got {major}.{minor}"
        assert minor >= 8, f"Python 3.8+ required, got 3.{minor}"
    
    def test_required_python_packages(self):
        """Test that required Python packages can be imported."""
        required_packages = [
            'fastapi',
            'pandas',
            'numpy',
            'uvicorn',
            'sqlalchemy',
            'pytest'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package '{package}' not available")
    
    def test_node_availability(self):
        """Test that Node.js is available for frontend."""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "Node.js not found"
            
            # Parse version (e.g., "v14.17.0" -> 14)
            version_str = result.stdout.strip()
            if version_str.startswith('v'):
                major_version = int(version_str[1:].split('.')[0])
                assert major_version >= 14, f"Node.js 14+ required, got {major_version}"
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available - skipping frontend tests")
    
    def test_npm_availability(self):
        """Test that npm is available."""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "npm not found"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("npm not available - skipping frontend tests")


class TestBasicInstallation:
    """Test basic installation flow."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_env_file_creation(self, temp_project_dir):
        """Test creation of .env file from example."""
        # Simulate the project structure
        backend_dir = temp_project_dir / "backend"
        backend_dir.mkdir()
        
        # Create .env.example file
        env_example = backend_dir / ".env.example"
        env_example.write_text("""
# API Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEFAULT_PROVIDER=openai

# Database
DATABASE_URL=sqlite:///data.db

# Logging
LOG_LEVEL=INFO
        """.strip())
        
        # Test copying .env.example to .env
        env_file = backend_dir / ".env"
        shutil.copy(env_example, env_file)
        
        assert env_file.exists(), ".env file should be created"
        content = env_file.read_text()
        assert "OPENAI_API_KEY" in content
        assert "DATABASE_URL" in content
    
    def test_backend_requirements_format(self):
        """Test that requirements.txt is properly formatted."""
        project_root = Path(__file__).parent.parent
        requirements_file = project_root / "backend" / "requirements.txt"
        
        if not requirements_file.exists():
            pytest.skip("requirements.txt not found")
        
        content = requirements_file.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Basic validation
        assert len(lines) > 0, "requirements.txt should not be empty"
        
        # Check for essential packages
        essential_packages = ['fastapi', 'pandas', 'uvicorn']
        found_packages = set()
        
        for line in lines:
            if not line.startswith('#'):
                package_name = line.split('==')[0].split('>=')[0].split('~=')[0]
                found_packages.add(package_name.lower())
        
        for package in essential_packages:
            assert package in found_packages, f"Essential package '{package}' not found in requirements.txt"
    
    def test_frontend_package_json_format(self):
        """Test that package.json is properly formatted."""
        project_root = Path(__file__).parent.parent
        package_json = project_root / "frontend" / "package.json"
        
        if not package_json.exists():
            pytest.skip("package.json not found")
        
        import json
        with open(package_json) as f:
            package_data = json.load(f)
        
        # Basic validation
        assert "name" in package_data, "package.json should have name field"
        assert "dependencies" in package_data, "package.json should have dependencies"
        
        # Check for essential packages
        essential_packages = ['react', 'react-dom']
        dependencies = package_data.get('dependencies', {})
        
        for package in essential_packages:
            assert package in dependencies, f"Essential package '{package}' not found in package.json"


class TestDeploymentScript:
    """Test the deployment script functionality."""
    
    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent
    
    def test_deploy_script_exists(self, project_root):
        """Test that deploy.sh script exists and is executable."""
        deploy_script = project_root / "deploy.sh"
        assert deploy_script.exists(), "deploy.sh script not found"
        assert os.access(deploy_script, os.X_OK), "deploy.sh should be executable"
    
    def test_deploy_script_help(self, project_root):
        """Test deploy script help functionality."""
        deploy_script = project_root / "deploy.sh"
        
        if not deploy_script.exists():
            pytest.skip("deploy.sh not found")
        
        try:
            result = subprocess.run([str(deploy_script), '--help'], 
                                  capture_output=True, text=True, timeout=30)
            # Script should either show help or run normally
            assert result.returncode in [0, 1, 2], f"Deploy script failed with code {result.returncode}"
        except subprocess.TimeoutExpired:
            pytest.fail("Deploy script help command timed out")


class TestServiceHealth:
    """Test service health and basic functionality."""
    
    @pytest.fixture(scope="class")
    def backend_process(self):
        """Start backend service for testing."""
        project_root = Path(__file__).parent.parent
        backend_dir = project_root / "backend"
        
        if not backend_dir.exists():
            pytest.skip("Backend directory not found")
        
        # Set test environment
        env = os.environ.copy()
        env.update({
            'TESTING': 'true',
            'OPENAI_API_KEY': 'test-key-for-testing',
            'DATABASE_URL': 'sqlite:///test.db',
            'LOG_LEVEL': 'WARNING'
        })
        
        try:
            # Start backend process
            process = subprocess.Popen([
                sys.executable, 'main.py', '--port', '8001'  # Use different port for testing
            ], cwd=backend_dir, env=env)
            
            # Give it time to start
            time.sleep(5)
            
            yield process
            
        except Exception as e:
            pytest.skip(f"Could not start backend process: {e}")
        finally:
            # Cleanup
            if 'process' in locals():
                process.terminate()
                process.wait()
    
    def test_backend_health_endpoint(self, backend_process):
        """Test that backend health endpoint responds."""
        try:
            response = requests.get('http://localhost:8001/api/v2/health', timeout=10)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            data = response.json()
            assert 'status' in data, "Health response should contain status"
            
        except requests.exceptions.ConnectionError:
            pytest.fail("Could not connect to backend service")
        except requests.exceptions.Timeout:
            pytest.fail("Backend health check timed out")
    
    def test_backend_api_docs(self, backend_process):
        """Test that API documentation is accessible."""
        try:
            response = requests.get('http://localhost:8001/docs', timeout=10)
            assert response.status_code == 200, f"API docs failed: {response.status_code}"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Could not connect to backend service")
        except requests.exceptions.Timeout:
            pytest.skip("API docs request timed out")


class TestSampleData:
    """Test sample data files."""
    
    def test_sample_data_directory_exists(self):
        """Test that sample data directory exists."""
        project_root = Path(__file__).parent.parent
        sample_data_dir = project_root / "sample_data"
        assert sample_data_dir.exists(), "sample_data directory not found"
    
    def test_sample_csv_files_exist(self):
        """Test that sample CSV files exist and are valid."""
        project_root = Path(__file__).parent.parent
        sample_data_dir = project_root / "sample_data"
        
        if not sample_data_dir.exists():
            pytest.skip("sample_data directory not found")
        
        csv_files = list(sample_data_dir.glob("*.csv"))
        assert len(csv_files) > 0, "No CSV files found in sample_data directory"
        
        # Test that files can be read as CSV
        import pandas as pd
        for csv_file in csv_files[:3]:  # Test first 3 files
            try:
                df = pd.read_csv(csv_file)
                assert not df.empty, f"CSV file {csv_file.name} is empty"
                assert len(df.columns) > 0, f"CSV file {csv_file.name} has no columns"
            except Exception as e:
                pytest.fail(f"Could not read CSV file {csv_file.name}: {e}")
    
    def test_sample_data_schema_consistency(self):
        """Test that sample data files have consistent schemas."""
        project_root = Path(__file__).parent.parent
        sample_data_dir = project_root / "sample_data"
        
        if not sample_data_dir.exists():
            pytest.skip("sample_data directory not found")
        
        csv_files = list(sample_data_dir.glob("*.csv"))
        if len(csv_files) < 2:
            pytest.skip("Not enough CSV files to test schema consistency")
        
        import pandas as pd
        
        # Read all CSV files and check for common columns
        all_columns = []
        for csv_file in csv_files[:3]:  # Test first 3 files
            try:
                df = pd.read_csv(csv_file)
                all_columns.append(set(df.columns))
            except Exception:
                continue  # Skip files that can't be read
        
        if len(all_columns) >= 2:
            # Check for common columns across files
            common_columns = set.intersection(*all_columns)
            assert len(common_columns) > 0, "Sample CSV files should have some common columns"


class TestDocumentation:
    """Test documentation files."""
    
    def test_readme_exists(self):
        """Test that README file exists."""
        project_root = Path(__file__).parent.parent
        readme_file = project_root / "README.md"
        assert readme_file.exists(), "README.md not found"
        
        content = readme_file.read_text()
        assert len(content) > 100, "README.md appears to be empty or too short"
        
        # Check for essential sections
        essential_sections = ["installation", "usage", "requirements"]
        content_lower = content.lower()
        
        for section in essential_sections:
            assert section in content_lower, f"README.md should contain '{section}' section"
    
    def test_license_file_exists(self):
        """Test that license file exists (optional)."""
        project_root = Path(__file__).parent.parent
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md']
        
        license_exists = any((project_root / license_file).exists() for license_file in license_files)
        if not license_exists:
            pytest.skip("License file not found (optional)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])