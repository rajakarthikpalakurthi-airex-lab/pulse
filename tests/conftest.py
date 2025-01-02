# tests/conftest.py
import pytest
from pathlib import Path
import yaml
from pdw_simulator.models import Scenario, Radar, Sensor
from pdw_simulator.scenario_geometry_functions import get_unit_registry

@pytest.fixture(scope="session")
def ureg():
    """Fixture to provide unit registry across all tests"""
    return get_unit_registry()

@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from YAML file"""
    config_path = Path(__file__).parent / "fixtures" / "test_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture
def scenario(test_config):
    """Create a test scenario"""
    return Scenario(test_config['scenario'])

@pytest.fixture
def radar(test_config):
    """Create a test radar"""
    return Radar(test_config['radars'][0])

@pytest.fixture
def sensor(test_config):
    """Create a test sensor"""
    return Sensor(test_config['sensors'][0])