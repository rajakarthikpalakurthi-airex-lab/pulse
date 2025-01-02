# tests/test_integration.py
import pytest
import numpy as np
from pdw_simulator.models import Scenario

class TestIntegration:
    def test_full_simulation(self, scenario, radar, sensor):
        """Test complete simulation workflow"""
        # Setup
        scenario.radars.append(radar)
        scenario.sensors.append(sensor)
        
        # Calculate trajectories
        radar.calculate_trajectory(scenario.end_time, scenario.time_step)
        sensor.calculate_trajectory(scenario.end_time, scenario.time_step)
        
        # Run simulation
        initial_time = scenario.current_time
        test_steps = 3
        
        for _ in range(test_steps):
            scenario.update()
            assert scenario.current_time <= scenario.end_time
            
        assert scenario.current_time == initial_time + (test_steps * scenario.time_step)

    def test_radar_sensor_interaction(self, radar, sensor, ureg):
        """Test radar and sensor interaction"""
        # Test pulse detection and measurement
        true_amplitude = -80 * ureg.dB
        # Don't create r as a Quantity since measure_amplitude will convert it
        r = 1000  # Changed from r = 1000 * ureg.meter
        P_theta = 0 * ureg.dB
        t = 0 * ureg.second
        P0 = 1000 * ureg.watt
        
        # Verify detection
        detected = sensor.detect_pulse(true_amplitude)
        if detected:
            # Verify measurements
            measured_amplitude = sensor.measure_amplitude(
                true_amplitude, r, P_theta, t, P0)
            assert isinstance(measured_amplitude.magnitude, (int, float))
            assert measured_amplitude.units == ureg.dB

    @pytest.mark.slow
    def test_long_simulation(self, test_config):
        """Test longer simulation for stability"""
        # Modify config for longer simulation
        long_config = test_config.copy()
        long_config['scenario']['end_time'] = 10.0
        
        scenario = Scenario(long_config['scenario'])
        # Add radars and sensors...
        
        # Run simulation and verify stability
        while scenario.current_time <= scenario.end_time:
            scenario.update()
            # Add assertions for state validity