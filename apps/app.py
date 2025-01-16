import streamlit as st
from styles import apply_custom_styles
import yaml
import subprocess
import os
import ast
import pandas as pd
import copy
import base64
import functools
import sys

# Must be the first Streamlit command and only called once
st.set_page_config(
    page_title="Pulse Descriptor Word Simulator",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
) 

# Rest of your imports
sys.path.append('/mnt/d/zenoxml/pulse/src')
from pdw_simulator.visualization import create_pdw_visualizer

def add_bg_from_local(image_file: str):
    """Optional: Adds background image if it exists."""
    if not os.path.isfile(image_file):
        st.error(f"Background image file '{image_file}' not found.")
        return
    with open(image_file, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def load_config():
    """
    Load config from 'dataconfig.yaml' if it exists, else return empty dict.
    We won't show a separate sensor UI; we force a single sensor if none is found.
    """
    if os.path.exists('config/tomlconfig.yaml'):
        with open('config/tomlconfig.yaml', 'r') as file:
            return yaml.safe_load(file)
    else:
        return {}

def save_config(config):
    """Save updated config to 'dataconfig.yaml'."""
    with open('config/tomlconfig.yaml', 'w') as file:
        yaml.dump(config, file)

def run_simulation():
    """
    Execute main.py to run the simulator.
    main.py is located in src/pdw_simulator/ according to your path.
    """
    main_path = os.path.join('src', 'pdw_simulator', 'main.py')
    if os.path.exists(main_path):
        subprocess.run(['python', main_path])
    else:
        st.error(f"main.py not found at {main_path}")

def display_output():
    """
    Display the PDW results, if any, from pdw.csv
    """
    st.subheader("PDW Data")
    if os.path.exists('pdw.csv'):
        pd.options.display.float_format = '{:.9e}'.format
        pdw_data = pd.read_csv('pdw.csv')

        tab1, tab2 = st.tabs(["Visualizations", "Raw Data"])

        with tab1:
            viz_container = st.container()
            visualizer = create_pdw_visualizer(viz_container)
            visualizer.update_data(pdw_data)
            visualizer.display(viz_container)
            if st.button("Refresh Visualization"):
                visualizer.update_data(pdw_data)

        with tab2:
            st.dataframe(pdw_data)
    else:
        st.error("pdw.csv not found. Please run the simulation first.")

def main():
    add_bg_from_local('utils/background_image.jpg')
    apply_custom_styles()
    st.title("Pulse Descriptor Word Simulator")

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 0
        st.session_state.config = load_config()  # Load from dataconfig.yaml
        st.session_state.num_radars = 0

    # --- Force exactly one default sensor if not present ---
    # (No sensor UI is shown; we either keep the first sensor or create a default.)
    if 'sensors' not in st.session_state.config:
        st.session_state.config['sensors'] = []
    if len(st.session_state.config['sensors']) < 1:
        st.session_state.config['sensors'] = [{
            'name': 'Sensor1',
            'start_position': [0, 0],
            'velocity': [0, 0],
            'start_time': 0,
            'saturation_level': '-70 dB',
            'detection_probability': {
                'level': [-80, -85, -90, -95],
                'probability': [100, 85, 60, 30]
            },
            'amplitude_error': {
                'systematic': {'type': 'constant', 'error': '0 dB'},
                'arbitrary': {'type': 'gaussian', 'error': '0.5 dB'}
            },
            'toa_error': {
                'systematic': {'type': 'constant', 'error': '0 s'},
                'arbitrary': {'type': 'gaussian', 'error': '1e-9 s'}
            },
            'frequency_error': {
                'systematic': {'type': 'linear', 'error': '0 Hz', 'rate': '100 Hz/s'},
                'arbitrary': {'type': 'gaussian', 'error': '1e6 Hz'}
            },
            'pulse_width_error': {
                'systematic': {'type': 'constant', 'error': '0 s'},
                'arbitrary': {'type': 'uniform', 'error': '2%'}
            },
            'aoa_error': {
                'systematic': {'type': 'constant', 'error': '0 deg'},
                'arbitrary': {'type': 'gaussian', 'error': '1 deg'}
            },
            'freq_padding_factor': 4
        }]
    # If more than one sensor is in config, keep only the first one
    st.session_state.config['sensors'] = st.session_state.config['sensors'][:1]

    # Navigation convenience
    def next_page():
        st.session_state.page += 1
    def prev_page():
        st.session_state.page -= 1
    def reset_app():
        st.session_state.page = 0

    # Page 0: Scenario Parameters
    if st.session_state.page == 0:
        st.header("Scenario Parameters")
        scenario = st.session_state.config.get('scenario', {})
        start_time = st.number_input('Start Time (s)',
                                     value=float(scenario.get('start_time', 0.0)),
                                     format="%.2f")
        end_time = st.number_input('End Time (s)',
                                   value=float(scenario.get('end_time', 10.0)),
                                   format="%.2f")
        time_step = st.number_input('Time Step (s)',
                                    value=float(scenario.get('time_step', 0.1)),
                                    format="%.4f")

        def save_scenario_params():
            st.session_state.config['scenario'] = {
                'start_time': start_time,
                'end_time': end_time,
                'time_step': time_step
            }
            next_page()

        col1, col2, col3 = st.columns([1, 6, 1])
        with col3:  # Next button on the right
            st.button("Next", on_click=save_scenario_params, key='scenario_next')

        # Page 1: Number of Radars
        # Page 1: Number of Radars
    elif st.session_state.page == 1:
        st.header("Select Number of Radars")
        num_radars = st.number_input(
            'Number of Radars',
            min_value=1,
            max_value=10,
            value=int(st.session_state.num_radars) if st.session_state.num_radars else 1,
            step=1
        )

        # Define the function before using it
        def save_num_radars():
            st.session_state.num_radars = num_radars
            # Truncate or expand radars list as needed
            st.session_state.config['radars'] = st.session_state.config.get('radars', [])[:num_radars]
            next_page()

        # Then use it in the button layout
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:  # Back button on the left
            st.button("Back", on_click=prev_page, key='radar_count_back')
        with col3:  # Next button on the right
            st.button("Next", on_click=save_num_radars, key='radar_count_next')


    # Radar config pages (one page per radar)
    elif st.session_state.page >= 2 and st.session_state.page < st.session_state.num_radars + 2:
        radar_index = st.session_state.page - 2
        radars = st.session_state.config.get('radars', [])

        # Ensure a radar entry is present at the correct index
        if len(radars) <= radar_index:
            if radar_index == 0:
                radars.append({'name': f'Radar{radar_index + 1}'})
            else:
                new_radar = copy.deepcopy(radars[0])  # Copy from first if you want consistency
                new_radar['name'] = f'Radar{radar_index + 1}'
                radars.append(new_radar)
            st.session_state.config['radars'] = radars

        radar = radars[radar_index]
        st.header(f"Configure {radar.get('name', f'Radar{radar_index + 1}')}")

        # Basic Info
        with st.expander("Basic Information", expanded=True):
            radar['name'] = st.text_input(
                'Radar Name',
                value=radar.get('name', f'Radar{radar_index + 1}'),
                key=f"radar_name_{radar_index}"
            )
            radar['power'] = st.number_input(
                "Power (W)",
                value=float(radar.get('power', 1000.0)),
                format="%.2f",
                key=f"radar_power_{radar_index}"
            )

        # Movement
        with st.expander("Movement Parameters", expanded=False):
            start_position_str = st.text_input(
                "Start Position (x, y in meters)",
                value=str(radar.get('start_position', [0, 0])),
                key=f"start_position_{radar_index}"
            )
            try:
                radar['start_position'] = ast.literal_eval(start_position_str)
            except:
                st.error("Invalid format for Start Position. e.g., [0, 0]")

            velocity_str = st.text_input(
                "Velocity (vx, vy in m/s)",
                value=str(radar.get('velocity', [0, 0])),
                key=f"velocity_{radar_index}"
            )
            try:
                radar['velocity'] = ast.literal_eval(velocity_str)
            except:
                st.error("Invalid format for Velocity. e.g., [0, 0]")

            radar['start_time'] = st.number_input(
                "Start Time (s)",
                value=float(radar.get('start_time', 0.0)),
                format="%.2f",
                key=f"radar_starttime_{radar_index}"
            )

        # Rotation
        with st.expander("Rotation Parameters", expanded=False):
            rotation_types = ['constant', 'varying']
            rotation_type_default = radar.get('rotation_type', 'constant')
            if rotation_type_default not in rotation_types:
                rotation_type_default = 'constant'
            radar['rotation_type'] = st.selectbox(
                "Rotation Type",
                rotation_types,
                index=rotation_types.index(rotation_type_default),
                key=f"rotation_type_{radar_index}"
            )
            radar['rotation_params'] = radar.get('rotation_params', {})

            radar['rotation_params']['t0'] = st.number_input(
                "Rotation t0",
                value=float(radar['rotation_params'].get('t0', 0.0)),
                format="%.2f",
                key=f"rot_t0_{radar_index}"
            )
            radar['rotation_params']['alpha0'] = st.number_input(
                "Initial Angle (rad)",
                value=float(radar['rotation_params'].get('alpha0', 0.0)),
                format="%.2f",
                key=f"rot_alpha0_{radar_index}"
            )
            radar['rotation_params']['T_rot'] = st.number_input(
                "Rotation Period (s)",
                value=float(radar['rotation_params'].get('T_rot', 2.5)),
                format="%.2f",
                key=f"rot_T_{radar_index}"
            )

            if radar['rotation_type'] == 'varying':
                radar['rotation_params']['A'] = st.number_input(
                    "Amplitude A",
                    value=float(radar['rotation_params'].get('A', 0.1)),
                    format="%.2f",
                    key=f"rotA_{radar_index}"
                )
                radar['rotation_params']['s'] = st.number_input(
                    "Angular Frequency s",
                    value=float(radar['rotation_params'].get('s', 1.0)),
                    format="%.2f",
                    key=f"rot_s_{radar_index}"
                )
                radar['rotation_params']['phi0'] = st.number_input(
                    "Start Phase φ₀ (rad)",
                    value=float(radar['rotation_params'].get('phi0', 0.0)),
                    format="%.2f",
                    key=f"rot_phi0_{radar_index}"
                )

        # PRI
        with st.expander("PRI Parameters", expanded=False):
            pri_types = ['fixed', 'stagger', 'switched', 'jitter']
            pri_type_default = radar.get('pri_type', 'fixed')
            if pri_type_default not in pri_types:
                pri_type_default = 'fixed'
            radar['pri_type'] = st.selectbox(
                "PRI Type",
                pri_types,
                index=pri_types.index(pri_type_default),
                key=f"pri_type_{radar_index}"
            )
            radar['pri_params'] = radar.get('pri_params', {})

            if radar['pri_type'] == 'fixed':
                radar['pri_params']['pri'] = st.number_input(
                    "PRI (s)",
                    value=float(radar['pri_params'].get('pri', 0.001)),
                    format="%.6f",
                    key=f"pri_fixed_{radar_index}"
                )
            elif radar['pri_type'] == 'stagger':
                pri_pattern_str = st.text_input(
                    "PRI Pattern (s)",
                    value=str(radar['pri_params'].get('pri_pattern', [0.001])),
                    key=f"pri_pattern_{radar_index}"
                )
                try:
                    radar['pri_params']['pri_pattern'] = ast.literal_eval(pri_pattern_str)
                except:
                    st.error("Invalid PRI Pattern format.")
            elif radar['pri_type'] == 'switched':
                pri_pattern_str = st.text_input(
                    "PRI Pattern (s)",
                    value=str(radar['pri_params'].get('pri_pattern', [0.001])),
                    key=f"pri_pattern_switched_{radar_index}"
                )
                try:
                    radar['pri_params']['pri_pattern'] = ast.literal_eval(pri_pattern_str)
                except:
                    st.error("Invalid PRI Pattern format.")
                repetitions_str = st.text_input(
                    "Repetitions",
                    value=str(radar['pri_params'].get('repetitions', [1])),
                    key=f"repetitions_pri_{radar_index}"
                )
                try:
                    radar['pri_params']['repetitions'] = ast.literal_eval(repetitions_str)
                except:
                    st.error("Invalid Repetitions format.")
            elif radar['pri_type'] == 'jitter':
                radar['pri_params']['mean_pri'] = st.number_input(
                    "Mean PRI (s)",
                    value=float(radar['pri_params'].get('mean_pri', 0.001)),
                    format="%.6f",
                    key=f"pri_mean_{radar_index}"
                )
                radar['pri_params']['jitter_percentage'] = st.number_input(
                    "Jitter Percentage (%)",
                    value=float(radar['pri_params'].get('jitter_percentage', 5.0)),
                    format="%.2f",
                    key=f"pri_jitter_{radar_index}"
                )

        # Frequency
        with st.expander("Frequency Parameters", expanded=False):
            frequency_types = ['fixed', 'stagger', 'switched', 'jitter']
            frequency_type_default = radar.get('frequency_type', 'fixed')
            if frequency_type_default not in frequency_types:
                frequency_type_default = 'fixed'
            radar['frequency_type'] = st.selectbox(
                "Frequency Type",
                frequency_types,
                index=frequency_types.index(frequency_type_default),
                key=f"freq_type_{radar_index}"
            )
            radar['frequency_params'] = radar.get('frequency_params', {})

            if radar['frequency_type'] == 'fixed':
                freq_val = radar['frequency_params'].get('frequency', 15e9)
                radar['frequency_params']['frequency'] = st.number_input(
                    "Frequency (Hz)",
                    value=float(freq_val),
                    format="%.2f",
                    key=f"freq_fixed_{radar_index}"
                )
            elif radar['frequency_type'] == 'stagger':
                freq_pattern_str = st.text_input(
                    "Frequency Pattern (Hz)",
                    value=str(radar['frequency_params'].get('frequency_pattern', [15e9])),
                    key=f"freq_pattern_stagger_{radar_index}"
                )
                try:
                    radar['frequency_params']['frequency_pattern'] = ast.literal_eval(freq_pattern_str)
                except:
                    st.error("Invalid Frequency Pattern format.")
            elif radar['frequency_type'] == 'switched':
                freq_pattern_str = st.text_input(
                    "Frequency Pattern (Hz)",
                    value=str(radar['frequency_params'].get('frequency_pattern', [15e9])),
                    key=f"freq_pattern_switched_{radar_index}"
                )
                try:
                    radar['frequency_params']['frequency_pattern'] = ast.literal_eval(freq_pattern_str)
                except:
                    st.error("Invalid Frequency Pattern format.")
                freq_reps_str = st.text_input(
                    "Repetitions",
                    value=str(radar['frequency_params'].get('repetitions', [1])),
                    key=f"freq_repetitions_{radar_index}"
                )
                try:
                    radar['frequency_params']['repetitions'] = ast.literal_eval(freq_reps_str)
                except:
                    st.error("Invalid Repetitions format.")
            elif radar['frequency_type'] == 'jitter':
                freq_mean = radar['frequency_params'].get('mean_frequency', 15e9)
                radar['frequency_params']['mean_frequency'] = st.number_input(
                    "Mean Frequency (Hz)",
                    value=float(freq_mean),
                    format="%.2f",
                    key=f"freq_mean_{radar_index}"
                )
                radar['frequency_params']['jitter_percentage'] = st.number_input(
                    "Jitter Percentage (%)",
                    value=float(radar['frequency_params'].get('jitter_percentage', 5.0)),
                    format="%.2f",
                    key=f"freq_jitter_{radar_index}"
                )

        # Pulse Width
        with st.expander("Pulse Width Parameters", expanded=False):
            pw_types = ['fixed', 'stagger', 'switched', 'jitter']
            pw_type_default = radar.get('pulse_width_type', 'fixed')
            if pw_type_default not in pw_types:
                pw_type_default = 'fixed'
            radar['pulse_width_type'] = st.selectbox(
                "Pulse Width Type",
                pw_types,
                index=pw_types.index(pw_type_default),
                key=f"pw_type_{radar_index}"
            )
            radar['pulse_width_params'] = radar.get('pulse_width_params', {})

            if radar['pulse_width_type'] == 'fixed':
                radar['pulse_width_params']['pulse_width'] = st.number_input(
                    "Pulse Width (s)",
                    value=float(radar['pulse_width_params'].get('pulse_width', 1e-6)),
                    format="%.8f",
                    key=f"pw_fixed_{radar_index}"
                )
            elif radar['pulse_width_type'] == 'stagger':
                pw_pattern_str = st.text_input(
                    "Pulse Width Pattern (s)",
                    value=str(radar['pulse_width_params'].get('pulse_width_pattern', [1e-6])),
                    key=f"pw_pattern_{radar_index}"
                )
                try:
                    radar['pulse_width_params']['pulse_width_pattern'] = ast.literal_eval(pw_pattern_str)
                except:
                    st.error("Invalid Pulse Width Pattern format.")
            elif radar['pulse_width_type'] == 'switched':
                pw_pattern_str = st.text_input(
                    "Pulse Width Pattern (s)",
                    value=str(radar['pulse_width_params'].get('pulse_width_pattern', [1e-6])),
                    key=f"pw_pattern_switched_{radar_index}"
                )
                try:
                    radar['pulse_width_params']['pulse_width_pattern'] = ast.literal_eval(pw_pattern_str)
                except:
                    st.error("Invalid Pulse Width Pattern format.")
                pw_reps_str = st.text_input(
                    "Repetitions",
                    value=str(radar['pulse_width_params'].get('repetitions', [1])),
                    key=f"pw_repetitions_switched_{radar_index}"
                )
                try:
                    radar['pulse_width_params']['repetitions'] = ast.literal_eval(pw_reps_str)
                except:
                    st.error("Invalid Repetitions format.")
            elif radar['pulse_width_type'] == 'jitter':
                mean_pw = radar['pulse_width_params'].get('mean_pulse_width', 1e-6)
                radar['pulse_width_params']['mean_pulse_width'] = st.number_input(
                    "Mean Pulse Width (s)",
                    value=float(mean_pw),
                    format="%.8f",
                    key=f"pw_mean_{radar_index}"
                )
                radar['pulse_width_params']['jitter_percentage'] = st.number_input(
                    "Jitter Percentage (%)",
                    value=float(radar['pulse_width_params'].get('jitter_percentage', 5.0)),
                    format="%.2f",
                    key=f"pw_jitter_{radar_index}"
                )

        # Lobe Pattern
        with st.expander("Lobe Pattern Parameters", expanded=False):
            radar['lobe_pattern'] = radar.get('lobe_pattern', {})
            radar['lobe_pattern']['type'] = st.selectbox(
                "Lobe Pattern Type",
                ['Sinc'],
                index=0,
                key=f"lobe_type_{radar_index}"
            )
            radar['lobe_pattern']['main_lobe_opening_angle'] = st.number_input(
                "Main Lobe Opening Angle (deg)",
                value=float(radar['lobe_pattern'].get('main_lobe_opening_angle', 5.0)),
                format="%.2f",
                key=f"lobe_main_{radar_index}"
            )
            radar['lobe_pattern']['radar_power_at_main_lobe'] = st.number_input(
                "Radar Power at Main Lobe (dB)",
                value=float(radar['lobe_pattern'].get('radar_power_at_main_lobe', 0.0)),
                format="%.2f",
                key=f"lobe_main_power_{radar_index}"
            )
            radar['lobe_pattern']['radar_power_at_back_lobe'] = st.number_input(
                "Radar Power at Back Lobe (dB)",
                value=float(radar['lobe_pattern'].get('radar_power_at_back_lobe', -20.0)),
                format="%.2f",
                key=f"lobe_back_power_{radar_index}"
            )

        col1, col2 = st.columns([1,1])

        def save_radar_config():
            st.session_state.config['radars'][radar_index] = radar
            next_page()

        col1.button("Next", on_click=functools.partial(save_radar_config), key=f'next_button_{st.session_state.page}')
        col2.button("Back", on_click=prev_page, key=f'back_button_{st.session_state.page}')

    # Jump to review
    elif st.session_state.page == st.session_state.num_radars + 2:
        st.header("Review Configuration")

        scenario_cfg = st.session_state.config.get('scenario', {})
        st.subheader("Scenario Configuration")
        st.write(f"**Start Time:** {scenario_cfg.get('start_time', 0.0)}")
        st.write(f"**End Time:** {scenario_cfg.get('end_time', 10.0)}")
        st.write(f"**Time Step:** {scenario_cfg.get('time_step', 0.1)}")

        st.subheader("Radar Configurations")
        for idx, radar in enumerate(st.session_state.config['radars']):
            st.write(f"### Radar {idx + 1}: {radar['name']}")
            st.json(radar)

        st.subheader("Sensor Configuration (Single Default Sensor Only)")
        st.json(st.session_state.config['sensors'][0])

        col1, col2 = st.columns([1,1])

        def run_simulation_and_next():
            save_config(st.session_state.config)
            run_simulation()
            next_page()

        col1.button("Run Simulation", on_click=run_simulation_and_next, key='run_simulation')
        col2.button("Back", on_click=prev_page, key='review_back')

    # Output
    elif st.session_state.page == st.session_state.num_radars + 3:
        st.header("Simulation Output")
        display_output()

        col1, col2 = st.columns([1,1])
        col1.button("Back", on_click=prev_page, key='output_back')
        col2.button("Restart", on_click=lambda: [reset_app()], key='restart')

    # Sidebars
    st.sidebar.button("Restart", on_click=lambda: reset_app(), key='sidebar_restart')

    def go_to_references():
        st.session_state.page = st.session_state.num_radars + 5

    st.sidebar.button("References", on_click=go_to_references, key='sidebar_references')

    if st.session_state.page == st.session_state.num_radars + 5:
        st.header("References")
        st.latex(r"""
\begin{aligned}
&\textbf{Reference 1:} \\
&\text{Opland, E. J. (2013). Clustering Evaluation for Deinterleaving. FFI-rapport 2013/00567.}
\end{aligned}
""")
        col1, col2 = st.columns([1,1])
        col1.button("Back", on_click=prev_page, key='references_back')
        col2.button("Restart", on_click=reset_app, key='references_restart')

if __name__ == "__main__":
    main()
