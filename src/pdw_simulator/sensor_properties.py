import numpy as np
from pdw_simulator.radar_properties import calculate_doppler_shift, calculate_relative_velocity, apply_doppler_effect
from pdw_simulator.scenario_geometry_functions import get_unit_registry

ureg = get_unit_registry()

###############################################################################
# Updated helper for random samples
###############################################################################
def get_random_sample(error_func, size=1):
    """
    Call 'val = error_func(size)', which might return:
      - A length-1 array of floats or Pint Quantities
      - A single float or a single Pint Quantity
    We then safely return the first element if it's truly array-like,
    or the scalar as is if it's not an array.

    This avoids the 'float object is not subscriptable' error in Pint
    by carefully checking if val.magnitude is array-like.
    """
    val = error_func(size)

    # Case 1: It's a Pint Quantity
    if isinstance(val, ureg.Quantity):
        # Check if the underlying magnitude is array-like or just a float
        if hasattr(val.magnitude, '__getitem__') and not np.isscalar(val.magnitude):
            # e.g. array of shape (size,)
            return val[0]
        else:
            # It's a single scalar quantity
            return val

    # Case 2: It's not a Pint Quantity, but might be a NumPy array of floats
    if hasattr(val, '__getitem__') and not isinstance(val, str):
        # Return the first element
        return val[0]

    # Case 3: It's just a single scalar float
    return val


def parse_value_and_unit(string_value):
    parts = string_value.split()
    if len(parts) == 2:
        value, unit = parts
    elif len(parts) == 1:
        value, unit = parts[0], ''
    else:
        raise ValueError(f"Invalid value/unit string: {string_value}")
    
    if value.endswith('%'):
        return float(value[:-1]) / 100, 'percent'
    else:
        return float(value), unit


def create_error_model(error_config):
    e_type = error_config['type']

    if e_type == 'constant':
        error_value, error_unit = parse_value_and_unit(error_config['error'])
        def constant_func(t):
            return error_value * ureg(error_unit)
        return constant_func

    elif e_type == 'linear':
        error_value, error_unit = parse_value_and_unit(error_config['error'])
        rate_value, rate_unit = parse_value_and_unit(error_config['rate'])
        def linear_func(t):
            return (error_value + rate_value * t.magnitude) * ureg(error_unit)
        return linear_func

    elif e_type == 'sinus':
        A_val, A_unit = parse_value_and_unit(error_config['amplitude'])
        f_val, f_unit = parse_value_and_unit(error_config['frequency'])
        if f_unit != 'Hz':
            raise ValueError(f"Frequency unit must be Hz, got {f_unit}")
        phi0 = float(error_config['phase'])
        def sinus_func(t):
            return A_val * np.sin(2*np.pi*f_val * t.magnitude + phi0) * ureg(A_unit)
        return sinus_func

    elif e_type == 'gaussian':
        error_value, error_unit = parse_value_and_unit(error_config['error'])
        def gaussian_func(size=1):
            arr = np.random.normal(0, error_value, size)
            if error_unit == 'percent':
                return arr * ureg.dimensionless
            else:
                return arr * ureg(error_unit)
        return gaussian_func

    elif e_type == 'uniform':
        error_value, error_unit = parse_value_and_unit(error_config['error'])
        def uniform_func(size=1):
            arr = np.random.uniform(-error_value, error_value, size)
            if error_unit == 'percent':
                return arr * ureg.dimensionless
            else:
                return arr * ureg(error_unit)
        return uniform_func

    else:
        raise ValueError(f"Unknown error type: {e_type}")


def detect_pulse(amplitude, detection_levels, detection_probabilities, saturation_level):
    if amplitude.to('dB').magnitude > saturation_level.to('dB').magnitude:
        return True
    
    for level, prob in zip(detection_levels, detection_probabilities):
        if amplitude.to('dB').magnitude > level.to('dB').magnitude:
            return np.random.random() < prob
    return False


def measure_amplitude(true_amplitude, r, P_theta, t, P0, amplitude_error_syst, amplitude_error_arb):
    r = ureg.Quantity(r).to(ureg.meter)
    P_theta = ureg.Quantity(P_theta).to(ureg.dB)
    P0 = ureg.Quantity(P0).to(ureg.watt)

    r_dimless = r / ureg.meter
    Pr = 20 * ureg.dB * np.log10(r_dimless.magnitude)
    P0_dB = 10 * ureg.dB * np.log10(P0.magnitude)

    P_syst = amplitude_error_syst(t).to(ureg.dB)
    P_arb_sample = get_random_sample(amplitude_error_arb, size=1)
    P_arb = ureg.Quantity(P_arb_sample).to(ureg.dB)

    total_mag = P0_dB.magnitude - Pr.magnitude + P_theta.magnitude + P_syst.magnitude + P_arb.magnitude
    measured_amplitude = ureg.Quantity(total_mag, ureg.dB)
    return measured_amplitude


def measure_toa(true_toa, r, t, toa_error_syst, toa_error_arb):
    c = 299792458 * ureg.meter / ureg.second
    rQ = ureg.Quantity(r).to(ureg.meter)
    delta_Tr = rQ / c

    TOA_syst = toa_error_syst(t)
    if TOA_syst.dimensionality == ureg.dimensionless:
        TOA_syst *= ureg.second

    TOA_arb_sample = get_random_sample(toa_error_arb, size=1)
    TOA_arb = ureg.Quantity(TOA_arb_sample)
    if TOA_arb.dimensionality == ureg.dimensionless:
        TOA_arb *= ureg.second

    measured_toa = true_toa + delta_Tr + TOA_syst + TOA_arb
    return measured_toa


def measure_frequency(true_frequency, t, current_time, frequency_error_syst, frequency_error_arb,
                      radar=None, sensor=None):
    measured_freq = true_frequency

    f_syst = frequency_error_syst(t)
    if f_syst.dimensionality == ureg.dimensionless:
        f_syst *= ureg.Hz

    f_arb_sample = get_random_sample(frequency_error_arb, size=1)
    f_arb = ureg.Quantity(f_arb_sample)
    if f_arb.dimensionality == ureg.dimensionless:
        f_arb *= ureg.Hz

    measured_freq += f_syst + f_arb

    if radar and sensor:
        measured_freq = apply_doppler_effect(measured_freq, radar, sensor)

    return measured_freq


def measure_pulse_width(true_pw, t, pw_error_syst, pw_error_arb):
    PW_syst = pw_error_syst(t)
    PW_arb_sample = get_random_sample(pw_error_arb, size=1)
    PW_arb = ureg.Quantity(PW_arb_sample)

    if PW_arb.dimensionality == ureg.dimensionless:
        PW_arb *= true_pw

    if PW_syst.dimensionality == ureg.dimensionless:
        PW_syst *= true_pw

    if true_pw.dimensionality == ureg.dimensionless:
        true_pw *= ureg.second

    measured_pw = true_pw + PW_syst + PW_arb
    return measured_pw.to(ureg.second)


def measure_aoa(true_aoa, t, aoa_error_syst, aoa_error_arb):
    """
    AOA measurement with safe random sampling to avoid 'float' object subscriptable.
    """
    AOA_syst = aoa_error_syst(t)
    AOA_arb_sample = get_random_sample(aoa_error_arb, size=1)
    AOA_arb = ureg.Quantity(AOA_arb_sample)

    measured_aoa = true_aoa + AOA_syst + AOA_arb
    return measured_aoa.to(ureg.degree)


def aoa_sinusoidal_error(AOA, A, f, AOA_ref):
    return A * np.sin(f * (AOA - AOA_ref))
