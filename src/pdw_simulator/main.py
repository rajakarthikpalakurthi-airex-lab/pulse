import yaml
import numpy as np
import sys
import os
import uuid
from datetime import datetime
import pandas as pd

sys.path.append('/mnt/d/zenoxml/pulse/src')

from pdw_simulator.scenario_geometry_functions import get_unit_registry
from pdw_simulator.radar_properties import *
from pdw_simulator.sensor_properties import *
from pdw_simulator.models import Scenario, Radar, Sensor
from pdw_simulator.data_export import PDWDataExporter
from timing import SimulationTimer

ureg = get_unit_registry()

def load_system_config():
    path = os.path.join('config', 'systemconfig.yaml')
    if not os.path.exists(path):
        print("No systemconfig.yaml found; using defaults.")
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_temp_config(system_config):
    temp_dir = system_config.get('directories', {}).get('temp', './temp')
    path = os.path.join(temp_dir, 'tempconfig.yaml')
    if not os.path.exists(path):
        raise FileNotFoundError(f"No tempconfig.yaml at {path}")
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
        if not data:
            raise ValueError("tempconfig.yaml is empty or invalid.")
        return data

###############################################################################
# Create scenario
###############################################################################
def create_scenario(config):
    if 'scenario' not in config:
        raise ValueError("Missing 'scenario' key in configuration.")
    scenario = Scenario(config['scenario'])
    
    # Build radars
    for radar_config in config.get('radars', []):
        radar = Radar(radar_config)
        radar.calculate_trajectory(scenario.end_time, scenario.time_step)
        scenario.radars.append(radar)

    # Build sensors
    for sensor_config in config.get('sensors', []):
        sensor = Sensor(sensor_config)  # Our updated sensor
        sensor.calculate_trajectory(scenario.end_time, scenario.time_step)
        scenario.sensors.append(sensor)
    
    return scenario

###############################################################################
# PDW generation logic
###############################################################################
def generate_pdw(sensor, radar, current_time):
    """
    Example function that uses sensor measurement logic.
    """
    # Geometry
    distance_vector = sensor.current_position - radar.current_position
    distance = np.linalg.norm(distance_vector) * ureg.meter
    distance = distance / ureg.meter
    angle = np.arctan2(distance_vector[1], distance_vector[0]) * ureg.radian

    # Check if a pulse is emitted
    time_window = 0.0001 * ureg.second
    pulse_time = radar.get_next_pulse_time(current_time)
    if pulse_time is None or pulse_time > current_time + time_window:
        return None

    # Convert to Pint
    true_toa = ureg.Quantity(pulse_time).to(ureg.second)
    true_amplitude = radar.calculate_power_at_angle(angle).to(ureg.dB)
    speed_of_light = 299792458 * ureg.meter / ureg.second
    true_toa += (distance / speed_of_light)
    true_frequency = radar.get_current_frequency()
    true_pw = radar.get_current_pulse_width()
    true_aoa = angle

    # Sensor detect + measure
    if sensor.detect_pulse(true_amplitude):
        measured_amplitude = sensor.measure_amplitude(true_amplitude, distance, true_amplitude, current_time, radar.power)
        measured_toa = sensor.measure_toa(true_toa, distance, current_time)
        measured_frequency = sensor.measure_frequency(true_frequency, current_time, radar)
        measured_pw = sensor.measure_pulse_width(true_pw, current_time)
        # The updated measure_aoa in sensor_properties ensures no float subscript error
        measured_aoa = sensor.measure_aoa(true_aoa, current_time)

        return {
            'TOA': measured_toa,
            'Amplitude': measured_amplitude,
            'Frequency': measured_frequency,
            'PulseWidth': measured_pw,
            'AOA': measured_aoa
        }
    return None

###############################################################################
# Run simulation
###############################################################################
def run_simulation(scenario, system_config):
    pdw_data_cfg = system_config['files']['pdw_data']
    output_dir = pdw_data_cfg['directory']
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    short_uuid = str(uuid.uuid4())[:8]
    base_name = pdw_data_cfg['base_name']
    ext = pdw_data_cfg['extension']

    filename = f"{base_name}{timestamp}_{short_uuid}{ext}"
    output_path = os.path.join(output_dir, filename)

    # Store PDWs
    times, sensor_ids, radar_ids = [], [], []
    toas, amplitudes, frequencies, pulse_widths, aoas = [], [], [], [], []

    while scenario.current_time <= scenario.end_time:
        scenario.update()
        for sensor in scenario.sensors:
            for radar in scenario.radars:
                pdw = generate_pdw(sensor, radar, scenario.current_time)
                if pdw:
                    times.append(scenario.current_time.magnitude)
                    sensor_ids.append(sensor.name)
                    radar_ids.append(radar.name)
                    toas.append(pdw['TOA'].magnitude)
                    amplitudes.append(pdw['Amplitude'].magnitude)
                    frequencies.append(pdw['Frequency'].magnitude)
                    pulse_widths.append(pdw['PulseWidth'].magnitude)
                    aoas.append(pdw['AOA'].magnitude)

        scenario.current_time += scenario.time_step

    pdw_data = pd.DataFrame({
        'Time': times,
        'SensorID': sensor_ids,
        'RadarID': radar_ids,
        'TOA': toas,
        'Amplitude': amplitudes,
        'Frequency': frequencies,
        'PulseWidth': pulse_widths,
        'AOA': aoas
    })

    pdw_data.to_csv(output_path, index=False)
    os.chmod(output_path, 0o666)

    print(f"Simulation complete. PDW data written to {output_path}")
    return output_path

###############################################################################
# main()
###############################################################################
def main():
    timer = SimulationTimer()
    timer.start_timer()

    system_config = load_system_config()
    sys.stdout = open('output.txt', 'w')

    try:
        with timer.time_section("Load Config"):
            config = load_temp_config(system_config)
            scenario = create_scenario(config)
        with timer.time_section("Simulation"):
            run_simulation(scenario, system_config)

        timer.print_report()
    except Exception as e:
        print(f"Error in simulation: {str(e)}")
        raise
    finally:
        sys.stdout.close()
        sys.stdout = sys.__stdout__

if __name__ == "__main__":
    main()
