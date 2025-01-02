# PULSE: Python Unified Library for Sensor Emulation

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

PULSE is a comprehensive Python library for synthetic sensor data generation, developed jointly by Zenteiq Aitech Innovations Private Limited and the AiREX (AI for Research and Engineering eXcellence) Lab at Indian Institute of Science, Bangalore. It provides a unified interface for simulating realistic datasets from various sensors and radars across multiple domains.

## Overview

PULSE enables developers, data scientists, and researchers to generate realistic sensor data for:
- Testing algorithms
- Validating data pipelines
- Prototyping IoT applications
- Simulating sensor networks
- Training and testing ML models

without the need for physical hardware.

## Features

- **Comprehensive Sensor Coverage**: Simulate data from dozens of sensor types across multiple domains
- **Configurable Parameters**: Adjustable settings for noise levels, ranges, and frequencies
- **Time-Series Generation**: Generate continuous or burst-based time-series data
- **Synthetic Anomalies**: Inject realistic anomalies for testing
- **Easy Integration**: Simple Python API for quick implementation

## Supported Domains and Sensors

### Air Monitoring
- Temperature, Humidity, Pressure
- Particulate Matter (PM2.5, PM10)
- Gas Sensors (CO, NOx, SO2)
- Doppler Weather Radar
- Lidar (Aerosol/Cloud Profiling)

### Sea Monitoring
- Buoy-Based Weather Sensors
- Water Quality Sensors
- Acoustic/Hydrophone
- Marine Radar
- Sonar Systems

### Ground Monitoring
- Seismic Sensors
- Ground-Penetrating Radar
- Soil Moisture Sensors
- Geophones

### Infrastructure Monitoring
- Strain Gauges
- Accelerometers
- Displacement Sensors
- Fiber-Optic Sensors
- Acoustic Emission Sensors
- Perimeter Radar

## Current Implementation

The current version includes:

### PDW (Pulse Descriptor Word) Simulator
- Located in `core/pdw-simulator/`
- Models radar-sensor interactions
- Generates Pulse Descriptor Words
- Includes configurable parameters and error models

## Installation

```bash
pip install pulse-sensor
```

## Quick Start

```python
from pulse import PDWSimulator

# Initialize PDW simulator
pdw_sim = PDWSimulator()

# Generate PDW data
pdw_data = pdw_sim.generate(
    duration=60,  # seconds
    pulse_rate=1000  # pulses per second
)

# Access generated data
print(pdw_data.head())
```

## Documentation

Detailed documentation is available at [docs link placeholder]. This includes:
- API Reference
- Usage Examples
- Parameter Configuration
- Simulation Tutorials

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code of Conduct
- Development Process
- Pull Request Protocol
- Testing Requirements

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use PULSE in your research, please cite:

```bibtex
@software{pulse2025,
  title = {PULSE: Python Unified Library for Sensor Emulation},
  author = {{Zenteiq Aitech Innovations} and {AiREX Lab}},
  year = {2025},
  url = {https://github.com/zenoxml/pulse}
}
```
## Official Partners

- [**ARTPARK**](https://artpark.in) (AI & Robotics Technology Park) at IISc
- In discussion with NVIDIA and other technology companies

## Acknowledgments

- Zenteiq Aitech Innovations Private Limited
- AiREX Lab at Indian Institute of Science, Bangalore

## Contact

- GitHub Issues: [https://github.com/zenoxml/pulse/issues](https://github.com/zenoxml/pulse/issues)
- Email: contact@scirex.org
