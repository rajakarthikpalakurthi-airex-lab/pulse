# tests/test_models.py
import pytest
import numpy as np
from pdw_simulator.models import Scenario, Radar, Sensor

class TestScenario:
    def test_initialization(self, scenario, ureg):
        """Test proper initialization of Scenario class"""
        assert scenario.start_time == 0.0 * ureg.second
        assert scenario.end_time == 1.0 * ureg.second
        assert scenario.time_step == 0.1 * ureg.second
        assert len(scenario.radars) == 0
        assert len(scenario.sensors) == 0

    def test_update(self, scenario, radar, sensor):
        """Test scenario update functionality"""
        scenario.radars.append(radar)
        scenario.sensors.append(sensor)
        initial_time = scenario.current_time
        scenario.update()
        assert scenario.current_time == initial_time + scenario.time_step

class TestRadar:
    def test_initialization(self, radar, ureg):
        """Test proper initialization of Radar class"""
        assert radar.name == 'TestRadar'
        assert radar.power == 1000.0 * ureg.watt
        np.testing.assert_array_equal(
            radar.start_position, 
            np.array([0, 0]) * ureg.meter
        )

    def test_pulse_generation(self, radar, scenario):
        """Test radar pulse generation"""
        radar.calculate_pulse_times(scenario.end_time)
        assert radar.pulse_times is not None
        assert len(radar.pulse_times) > 0
        assert all(t >= 0 for t in radar.pulse_times)

class TestSensor:
    def test_initialization(self, sensor, ureg):
        """Test proper initialization of Sensor class"""
        assert sensor.name == 'TestSensor'
        np.testing.assert_array_equal(
            sensor.start_position, 
            np.array([500, 500]) * ureg.meter
        )
        assert sensor.saturation_level == -70 * ureg.dB

    def test_detection(self, sensor, ureg):
        """Test sensor detection functionality"""
        test_amplitude = -85 * ureg.dB
        detection = sensor.detect_pulse(test_amplitude)
        assert isinstance(detection, bool)