# Contributing to PULSE

Thank you for your interest in contributing to PULSE (Python Unified Library for Sensor Emulation)! We welcome contributions from both academic and industrial communities.

## Table of Contents

- [Code Organization](#code-organization)
- [Coding Standards](#coding-standards)
- [Development Process](#development-process)
- [Documentation Guidelines](#documentation-guidelines)
- [Testing Requirements](#testing-requirements)
- [Legal Notices](#legal-notices)

## Code Organization

### Project Structure
```
pulse/
├── pulse/
│   ├── common/           # Common utilities and configurations
│   ├── sensors/          # Sensor simulation implementations
│   │   ├── air/         # Air monitoring sensors
│   │   ├── sea/         # Sea monitoring sensors
│   │   ├── ground/      # Ground monitoring sensors
│   │   ├── infrastructure/  # Infrastructure sensors
│   │   └── radar/       # Radar and PDW simulation
│   └── utils/           # Utility functions
├── tests/               # Test files
├── docs/                # Documentation
└── examples/            # Example scripts

Please see our [Project Structure](PROJECT_STRUCTURE.md) for more details.
```

### File Naming Conventions

1. **Python Files**
   - Use lowercase with underscores
   - Should be descriptive and specific
   - Examples:
     ```
     temperature_sensor.py
     doppler_radar.py
     water_quality_monitor.py
     ```

2. **Test Files**
   - Prefix with `test_`
   - Mirror the structure of source files
   - Examples:
     ```
     test_temperature_sensor.py
     test_doppler_radar.py
     ```

3. **Example Files**
   - Use descriptive names with purpose
   - Include sensor type in name
   - Examples:
     ```
     weather_station_demo.py
     marine_radar_simulation.py
     ```

## Coding Standards

### Python Style Guide

1. **General Guidelines**
   - Follow PEP 8
   - Use 4 spaces for indentation
   - Maximum line length: 88 characters (using Black formatter)

2. **Naming Conventions**
   ```python
   # Classes: CamelCase
   class TemperatureSensor:
       pass

   # Functions and variables: lowercase_with_underscores
   def calculate_sensor_reading():
       sensor_value = 0
       return sensor_value

   # Constants: UPPERCASE_WITH_UNDERSCORES
   MAX_TEMPERATURE = 100
   ```

3. **Docstring Format**
   ```python
   def generate_pdw_data(
       frequency: float,
       pulse_width: float,
       pri: float
   ) -> np.ndarray:
       """Generate Pulse Descriptor Word data.

       Args:
           frequency (float): Carrier frequency in Hz
           pulse_width (float): Pulse width in seconds
           pri (float): Pulse Repetition Interval in seconds

       Returns:
           np.ndarray: Generated PDW data array

       Raises:
           ValueError: If parameters are out of valid ranges

       Example:
           >>> pdw_data = generate_pdw_data(1e9, 1e-6, 1e-3)
           >>> print(pdw_data.shape)
           (1000, 4)
       """
   ```

4. **Comments and Documentation**
   - Add header to each file:
   ```python
   # Copyright (c) 2024 Zenteiq Aitech Innovations Private Limited and 
   # AiREX Lab, Indian Institute of Science, Bangalore.
   """
   Temperature sensor simulation module.
   
   This module implements various temperature sensor models with 
   configurable noise characteristics and sampling rates.
   """
   ```

### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import numpy as np
import pandas as pd

# Local imports
from pulse.common import config
from pulse.utils import noise_models
```

## Development Process

1. **Setting Up Development Environment**
   ```bash
   # Clone repository
   git clone https://github.com/zenoxml/pulse.git
   cd pulse

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows

   # Install dependencies
   pip install -e ".[dev,test]"
   ```

2. **Pre-commit Checks**
   ```bash
   # Install pre-commit hooks
   pre-commit install

   # Run manually
   pre-commit run --all-files
   ```

3. **Running Tests**
   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_pdw_simulator.py

   # Run with coverage
   pytest --cov=pulse tests/
   ```

## Documentation Guidelines

### API Documentation

1. **Module Documentation**
   ```python
   """
   PDW Simulator Module

   This module implements Pulse Descriptor Word generation with
   configurable radar parameters and noise models.

   Key Classes:
       PDWSimulator: Main simulator class
       RadarModel: Radar characteristics model
       ErrorModel: Error injection model

   Example:
       >>> simulator = PDWSimulator()
       >>> pdw_data = simulator.generate(duration=1.0)
   """
   ```

2. **Class Documentation**
   ```python
   class PDWSimulator:
       """
       Pulse Descriptor Word Simulator.

       Generates synthetic PDW data based on radar parameters
       and error models.

       Attributes:
           frequency (float): Carrier frequency in Hz
           pulse_width (float): Pulse width in seconds
           pri (float): Pulse Repetition Interval

       Example:
           >>> sim = PDWSimulator(frequency=1e9)
           >>> data = sim.generate()
       """
   ```

### Example Documentation
- Include purpose and usage
- Show expected output
- Explain key parameters
- Provide sample code

## Testing Requirements

1. **Unit Tests**
   - Test each class and function
   - Cover edge cases
   - Test error conditions
   - Verify parameter ranges

2. **Integration Tests**
   - Test sensor combinations
   - Verify data pipeline
   - Test system interfaces

3. **Performance Tests**
   - Measure execution time
   - Check memory usage
   - Verify data generation rates

## Legal Notices

- All contributions must be licensed under Apache License 2.0
- Include copyright notice in each file
- Sign Contributor License Agreement
- Maintain all attributions

---

*This document is maintained by the PULSE team at Zenteiq Aitech Innovations and AiREX Lab.*