# PULSE Project Structure

This document outlines the organization and structure of the PULSE (Python Unified Library for Sensor Emulation) project.

## Directory Structure

```
pulse/
├── LICENSE
├── README.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── setup.py
├── docs/
│   ├── api/
│   ├── examples/
│   ├── tutorials/
│   └── conf.py
├── tests/
│   ├── __init__.py
│   ├── test_air_sensors.py
│   ├── test_sea_sensors.py
│   └── test_ground_sensors.py
├── pulse/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── utils.py
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── air/
│   │   │   ├── __init__.py
│   │   │   ├── weather.py
│   │   │   ├── particulate.py
│   │   │   ├── gas.py
│   │   │   ├── doppler.py
│   │   │   └── lidar.py
│   │   ├── sea/
│   │   │   ├── __init__.py
│   │   │   ├── buoy.py
│   │   │   ├── water_quality.py
│   │   │   ├── hydrophone.py
│   │   │   ├── marine_radar.py
│   │   │   └── sonar.py
│   │   ├── ground/
│   │   │   ├── __init__.py
│   │   │   ├── seismic.py
│   │   │   ├── gpr.py
│   │   │   ├── soil.py
│   │   │   └── geophone.py
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── strain.py
│   │   │   ├── accelerometer.py
│   │   │   ├── displacement.py
│   │   │   └── fiber_optic.py
│   │   └── radar/
│   │       ├── __init__.py
│   │       ├── pdw_simulator.py
│   │       ├── models.py
│   │       └── utils.py
│   └── utils/
│       ├── __init__.py
│       ├── data_generation.py
│       ├── noise_models.py
│       └── validation.py
├── examples/
│   ├── pdw_simulation.py
│   ├── weather_simulation.py
│   ├── marine_radar_demo.py
│   └── multi_sensor_demo.py
└── notebooks/
    ├── quickstart.ipynb
    ├── pdw_analysis.ipynb
    └── sensor_visualization.ipynb
```

## Directory Descriptions

### Root Level

- `LICENSE`: Apache 2.0 license file
- `README.md`: Project overview and documentation
- `PROJECT_STRUCTURE.md`: This file
- `requirements.txt`: Project dependencies
- `setup.py`: Package installation and distribution configuration

### Main Package (`pulse/`)

#### Common Module (`common/`)
- `config.py`: Configuration management
- `utils.py`: Common utility functions

#### Sensors Module (`sensors/`)
Each sensor domain has its own subdirectory with specific implementations:

- `air/`: Air monitoring sensors (weather, particulate matter, gas, etc.)
- `sea/`: Sea monitoring sensors (buoy, water quality, sonar, etc.)
- `ground/`: Ground monitoring sensors (seismic, GPR, soil moisture, etc.)
- `infrastructure/`: Infrastructure monitoring sensors (strain, accelerometer, etc.)
- `radar/`: Radar simulation components including PDW simulator
  - `pdw_simulator.py`: PDW generation and simulation
  - `models.py`: Data models and structures
  - `utils.py`: Radar-specific utilities

#### Utilities (`utils/`)
- `data_generation.py`: Common data generation functions
- `noise_models.py`: Noise simulation models
- `validation.py`: Data validation utilities

### Documentation (`docs/`)
- `api/`: API reference documentation
- `examples/`: Example code and usage
- `tutorials/`: Step-by-step tutorials
- `conf.py`: Sphinx configuration

### Tests (`tests/`)
- Unit tests organized by module
- Integration tests
- Test utilities and fixtures

### Examples and Demos
- `examples/`: Standalone example scripts
- `notebooks/`: Jupyter notebooks for interactive demos

## Key Components

### Sensor Simulators
Each sensor type is implemented as a separate module with:
- Parameter configuration
- Data generation models
- Noise and error injection
- Output formatting

### PDW Simulator
The PDW simulator is implemented in `pulse/sensors/radar/` and includes:
- Pulse generation
- Radar-sensor interaction modeling
- Error and noise simulation
- Data output formatting

### Utility Functions
Common functionality is provided through utility modules:
- Data generation helpers
- Noise models
- Validation functions
- Configuration management

## Development Guidelines

1. Follow the existing directory structure when adding new features
2. Place tests in the corresponding test directory
3. Update documentation when adding new functionality
4. Include examples for new features
5. Maintain consistency with existing code style

## Future Extensions

The project structure supports easy addition of:
- New sensor types
- Additional simulation models
- Extended utility functions
- More examples and tutorials

For detailed development guidelines, please refer to the CONTRIBUTING.md file.
