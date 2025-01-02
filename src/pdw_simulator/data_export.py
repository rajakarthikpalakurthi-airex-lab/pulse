# data_export.py
import os
import h5py
import pandas as pd
import numpy as np
from datetime import datetime

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

    def estimate_data_size(self, pdw_data: pd.DataFrame) -> float:
        """Estimate the size of the data in MB"""
        return pdw_data.memory_usage(deep=True).sum() / (1024 * 1024)

    def export_to_csv(self, pdw_data: pd.DataFrame, filename: str):
        """Export data to CSV format"""
        pdw_data.to_csv(filename, index=False)
        # Save metadata separately
        metadata_file = filename.replace('.csv', '_metadata.csv')
        pd.DataFrame([self.metadata]).to_csv(metadata_file, index=False)

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
                # Create compressed dataset for each column
                data_group.create_dataset(
                    column,
                    data=pdw_data[column].values,
                    compression='gzip',
                    compression_opts=9  # Maximum compression
                )

    def export_data(self, pdw_data: pd.DataFrame, base_filename: str):
        """
        Export PDW data to appropriate format based on size
        
        Args:
            pdw_data: DataFrame containing PDW data
            base_filename: Base filename without extension
        """
        estimated_size = self.estimate_data_size(pdw_data)
        
        if estimated_size < self.size_threshold_mb:
            # Use CSV for smaller datasets
            filename = f"{base_filename}.csv"
            self.export_to_csv(pdw_data, filename)
            return filename
        else:
            # Use HDF5 for larger datasets
            filename = f"{base_filename}.h5"
            self.export_to_hdf5(pdw_data, filename)
            return filename

    def read_data(self, filename: str) -> pd.DataFrame:
        """
        Read PDW data from either CSV or HDF5 format
        
        Args:
            filename: Path to the data file
        Returns:
            DataFrame containing PDW data
        """
        if filename.endswith('.csv'):
            return pd.read_csv(filename)
        elif filename.endswith('.h5'):
            with h5py.File(filename, 'r') as f:
                # Read data from HDF5 file
                data_dict = {}
                for column in f['data'].keys():
                    data_dict[column] = f['data'][column][:]
                return pd.DataFrame(data_dict)
        else:
            raise ValueError("Unsupported file format")

    def set_metadata(self, sample_rate: float = None, ref_level: float = None):
        """Set metadata for the export"""
        if sample_rate is not None:
            self.metadata['samp_rate'] = sample_rate
        if ref_level is not None:
            self.metadata['ref_level'] = ref_level