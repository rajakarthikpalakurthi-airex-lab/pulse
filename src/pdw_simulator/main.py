import yaml
import numpy as np
import sys
sys.path.append('/mnt/d/zenoxml/pulse/src')
# from pdw_simulator.scenario_geometry_functions import calculate_trajectory, get_unit_registry
# from pdw_simulator.radar_properties import *
# from pdw_simulator.sensor_properties import *
# from pdw_simulator.models import Scenario, Radar, Sensor
from pdw_simulator.scenario_geometry_functions import calculate_trajectory, get_unit_registry
from pdw_simulator.scenario_geometry_functions import calculate_trajectory, get_unit_registry
from pdw_simulator.radar_properties import *
from pdw_simulator.sensor_properties import *
from pdw_simulator.models import Scenario, Radar, Sensor
from pdw_simulator.data_export import PDWDataExporter
import sys
import pandas as pd
from timing import SimulationTimer

sys.stdout=open('output.txt','wt')
# Get the unit registry from scenario_geometry_functions
ureg = get_unit_registry()



def load_config(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def create_scenario(config):
    scenario = Scenario(config['scenario'])
    
    for radar_config in config['radars']:
        radar = Radar(radar_config)
        radar.calculate_trajectory(scenario.end_time, scenario.time_step)
        scenario.radars.append(radar)
        # print(f"Added {radar.name} to scenario")
    
    for sensor_config in config['sensors']:
        sensor = Sensor(sensor_config)
        sensor.calculate_trajectory(scenario.end_time, scenario.time_step)
        scenario.sensors.append(sensor)
    
    return scenario


def run_simulation(scenario, output_base_filename):
    """
    Run the PDW simulation with adaptive file format selection.

    :param scenario: Scenario object containing radars and sensors
    :param output_base_filename: Base filename without extension for output
    """
    # Create lists to store all the data
    times = []
    sensor_ids = []
    radar_ids = []
    toas = []
    amplitudes = []
    frequencies = []
    pulse_widths = []
    aoas = []

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

    # Create DataFrame from collected data
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

    # Initialize exporter with 100MB threshold
    exporter = PDWDataExporter(size_threshold_mb=100)
    
    # Set metadata if available
    exporter.set_metadata(
        sample_rate=1/scenario.time_step.magnitude,  # Convert time step to sample rate
        ref_level=None  # Add reference level if available in your scenario
    )
    
    # Export data
    output_file = exporter.export_data(pdw_data, output_base_filename)
    
    return output_file


def generate_pdw(sensor, radar, current_time):
    # Calculate distance and angle between radar and sensor
    distance_vector = sensor.current_position - radar.current_position
    distance = np.linalg.norm(distance_vector) * ureg.meter
    distance=distance/ureg.meter
    angle = np.arctan2(distance_vector[1], distance_vector[0]) * ureg.radian

    # Check if a pulse is emitted at this time
    time_window = 0.0001 * ureg.second  # 100 microsecond window
    pulse_time = radar.get_next_pulse_time(current_time)
    # print(f"Next pulse time for {radar.name}: {pulse_time}")
    if pulse_time is None or pulse_time > current_time + time_window:
        # print(f"No pulse generated for {radar.name} at {current_time}")
        return None

    # Ensure pulse_time is a Pint Quantity
    pulse_time = ureg.Quantity(pulse_time).to(ureg.second)

    # Calculate true pulse parameters
    true_amplitude = radar.calculate_power_at_angle(angle).to(ureg.dB)
    speed_of_light = 299792458 * ureg.meter / ureg.second
    # print(f"Speed of light dimensionality: {speed_of_light.dimensionality}")
    # print(f"Pulse Time :{pulse_time.dimensionality}")
    # print(f"Distance Dimensionality: {distance.dimensionality}")
    true_toa = pulse_time + (distance / speed_of_light)
    true_frequency = radar.get_current_frequency()
    true_pw = radar.get_current_pulse_width()
    true_aoa = angle

    # Apply sensor detection and measurement
    if sensor.detect_pulse(true_amplitude):
        measured_amplitude = sensor.measure_amplitude(true_amplitude, distance, true_amplitude, current_time, radar.power)
        measured_toa = sensor.measure_toa(true_toa, distance, current_time)
        # measured_frequency = sensor.measure_frequency(true_frequency, current_time)
        measured_frequency = sensor.measure_frequency(true_frequency,current_time,radar)
        measured_pw = sensor.measure_pulse_width(true_pw, current_time)
        measured_aoa = sensor.measure_aoa(true_aoa, current_time)

        return {
            'TOA': measured_toa,
            'Amplitude': measured_amplitude,
            'Frequency': measured_frequency,
            'PulseWidth': measured_pw,
            'AOA': measured_aoa
        }
    else:
        return None


# def main():
#     config = load_config('dataconfig.yaml')
#     scenario = create_scenario(config)
    
#     output_base_filename = 'pdw'  # Will automatically add .csv or .h5 extension
#     output_file = run_simulation(scenario, output_base_filename)
    
#     print(f"Simulation complete. PDW data written to {output_file}")
def main():
    # Initialize timer
    timer = SimulationTimer()
    timer.start_timer()
    
    with timer.time_section("Configuration Loading"):
        config = load_config('config/tomlconfig.yaml')
        scenario = create_scenario(config)
    
    with timer.time_section("Simulation"):
        output_base_filename = 'pdw'
        
        # Create lists to store all the data
        with timer.time_section("Data Structure Initialization"):
            times = []
            sensor_ids = []
            radar_ids = []
            toas = []
            amplitudes = []
            frequencies = []
            pulse_widths = []
            aoas = []

        with timer.time_section("Main Simulation Loop"):
            while scenario.current_time <= scenario.end_time:
                with timer.time_section("Time Step Update"):
                    scenario.update()

                with timer.time_section("PDW Generation"):
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

        with timer.time_section("Data Export"):
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

            exporter = PDWDataExporter(size_threshold_mb=100)
            exporter.set_metadata(
                sample_rate=1/scenario.time_step.magnitude
            )
            output_file = exporter.export_data(pdw_data, output_base_filename)

    # Print and save timing report
    timer.print_report()
    timer.save_report('simulation_timing.yaml')
    
    return output_file
    

if __name__ == "__main__":
    main()

