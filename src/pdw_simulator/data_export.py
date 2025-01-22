import os
import h5py
import yaml
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

class SystemConfig:
    def __init__(self, config_path="config/systemconfig.yaml"):
        """Initialize system configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        if self.config['permissions']['output_files']['auto_create']:
            for dir_path in self.config['directories'].values():
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for specific file types
            for file_config in self.config['files'].values():
                Path(file_config['directory']).mkdir(parents=True, exist_ok=True)

    def generate_filename(self, file_type):
        """Generate a filename based on configuration"""
        file_config = self.config['files'][file_type]
        uuid_str = str(uuid.uuid4())
        
        if self.config['uuid']['format'] == 'timestamp_uuid':
            timestamp = datetime.now().strftime(self.config['uuid']['timestamp_format'])
            uuid_part = f"{timestamp}_{uuid_str}"
        else:
            uuid_part = uuid_str

        if self.config['uuid']['case'] == 'upper':
            uuid_part = uuid_part.upper()
        
        filename = f"{file_config['base_name']}{uuid_part}{file_config['extension']}"
        return os.path.join(file_config['directory'], filename)

    def cleanup_old_files(self, file_type):
        """Clean up old files based on configuration"""
        if not self.config['cleanup']['auto_cleanup']:
            return

        file_config = self.config['files'][file_type]
        if not file_config['preserve_history']:
            return

        directory = Path(file_config['directory'])
        files = sorted(directory.glob(f"{file_config['base_name']}*{file_config['extension']}"),
                      key=os.path.getctime, reverse=True)

        # Keep only the specified number of files
        max_history = file_config['max_history']
        for file in files[max_history:]:
            if not any(file.match(pattern) for pattern in self.config['cleanup']['exclude_patterns']):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")

class PDWDataExporter:
    def __init__(self, size_threshold_mb=100):
        """
        Initialize PDW Data Exporter
        
        Args:
            size_threshold_mb (int): Size threshold in MB to switch from CSV to HDF5
        """
        self.size_threshold_mb = size_threshold_mb
        self.metadata = {
            'time_unix': int(datetime.now().timestamp()),
            'time_py': str(datetime.now()),
            'samp_rate': None,
            'ref_level': None
        }
        self.system_config = SystemConfig()

    def estimate_data_size(self, pdw_data: pd.DataFrame) -> float:
        """Estimate the size of the data in MB"""
        return pdw_data.memory_usage(deep=True).sum() / (1024 * 1024)

    def export_to_csv(self, pdw_data: pd.DataFrame, filename: str):
        """Export data to CSV format"""
        pdw_data.to_csv(filename, index=False)
        
        # Save metadata with corresponding UUID
        base_name = os.path.splitext(os.path.basename(filename))[0]
        metadata_filename = self.system_config.generate_filename('metadata')
        pd.DataFrame([{**self.metadata, 'pdw_file': base_name}]).to_csv(metadata_filename, index=False)

    def export_to_hdf5(self, pdw_data: pd.DataFrame, filename: str):
        """Export data to HDF5 format with compression"""
        with h5py.File(filename, 'w') as f:
            # Create metadata group
            meta_group = f.create_group('metadata')
            for key, value in self.metadata.items():
                meta_group.attrs[key] = value

            # Create data group with datasets for each column
            data_group = f.create_group('data')
            for column in pdw_data.columns:
                data_group.create_dataset(
                    column,
                    data=pdw_data[column].values,
                    compression='gzip',
                    compression_opts=9
                )

    def export_data(self, pdw_data: pd.DataFrame):
        """Export PDW data to appropriate format based on size"""
        estimated_size = self.estimate_data_size(pdw_data)
        
        # Generate filename using system config
        filename = self.system_config.generate_filename('pdw_data')
        
        if estimated_size < self.size_threshold_mb:
            self.export_to_csv(pdw_data, filename)
        else:
            # Change extension for HDF5
            filename = os.path.splitext(filename)[0] + '.h5'
            self.export_to_hdf5(pdw_data, filename)
        
        # Clean up old files
        self.system_config.cleanup_old_files('pdw_data')
        
        return filename

    def set_metadata(self, sample_rate: float = None, ref_level: float = None):
        """Set metadata for the export"""
        if sample_rate is not None:
            self.metadata['samp_rate'] = sample_rate
        if ref_level is not None:
            self.metadata['ref_level'] = ref_level