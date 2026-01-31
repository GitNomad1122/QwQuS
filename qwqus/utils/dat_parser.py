"""
Parser for QUCS .dat files
"""
import re
from typing import Dict, List, Union
import numpy as np


class DatParser:
    """
    Parser for QUCS .dat output files
    """
    
    @staticmethod
    def parse_dat_file(file_path: str) -> Dict[str, Union[List, np.ndarray]]:
        """
        Parse a QUCS .dat file and return a dictionary of variables and their values
        """
        data = {}
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        current_var = None
        current_values = []
        
        for line in lines:
            line = line.strip()
            
            # Look for variable declaration
            if line.startswith('Symbol'):
                # Extract variable name
                parts = line.split()
                if len(parts) >= 2:
                    # Store previous variable if exists
                    if current_var and current_values:
                        data[current_var] = np.array(current_values)
                    
                    # Start new variable
                    current_var = parts[1].strip()
                    current_values = []
            
            # Skip Values header line
            elif line.startswith('Values'):
                continue
            
            # Handle end of variable or comment lines
            elif line.startswith('#') or line == '':
                if current_var and current_values:
                    data[current_var] = np.array(current_values)
                    current_var = None
                    current_values = []
            
            # Parse numeric values
            else:
                try:
                    # Handle complex numbers (real,imag format)
                    if ',' in line:
                        real, imag = map(float, line.split(','))
                        current_values.append(complex(real, imag))
                    # Handle regular numbers
                    else:
                        current_values.append(float(line))
                except ValueError:
                    # Skip lines that aren't numeric
                    continue
        
        # Don't forget the last variable
        if current_var and current_values:
            data[current_var] = np.array(current_values)
        
        return data
    
    @staticmethod
    def parse_raw_dat_content(content: str) -> Dict[str, Union[List, np.ndarray]]:
        """
        Parse raw .dat file content string
        """
        data = {}
        lines = content.splitlines()
        
        current_var = None
        current_values = []
        
        for line in lines:
            line = line.strip()
            
            # Look for variable declaration
            if line.startswith('Symbol'):
                # Extract variable name
                parts = line.split()
                if len(parts) >= 2:
                    # Store previous variable if exists
                    if current_var and current_values:
                        data[current_var] = np.array(current_values)
                    
                    # Start new variable
                    current_var = parts[1].strip()
                    current_values = []
            
            # Skip Values header line
            elif line.startswith('Values'):
                continue
            
            # Handle end of variable or comment lines
            elif line.startswith('#') or line == '':
                if current_var and current_values:
                    data[current_var] = np.array(current_values)
                    current_var = None
                    current_values = []
            
            # Parse numeric values
            else:
                try:
                    # Handle complex numbers (real,imag format)
                    if ',' in line:
                        real, imag = map(float, line.split(','))
                        current_values.append(complex(real, imag))
                    # Handle regular numbers
                    else:
                        current_values.append(float(line))
                except ValueError:
                    # Skip lines that aren't numeric
                    continue
        
        # Don't forget the last variable
        if current_var and current_values:
            data[current_var] = np.array(current_values)
        
        return data
    
    @staticmethod
    def get_frequency_response(data: Dict) -> tuple:
        """
        Extract frequency response from simulation data
        Returns (frequencies, magnitude, phase) if available
        """
        frequencies = None
        magnitude = None
        phase = None
        
        # Look for frequency variable
        for key in data:
            if 'freq' in key.lower() or 'indep' in key.lower():
                frequencies = data[key]
                break
        
        # Look for output variables (usually voltage or current)
        for key in data:
            if key != 'frequency' and 'v(' in key.lower():
                values = data[key]
                if frequencies is not None and len(values) == len(frequencies):
                    if all(isinstance(v, complex) for v in values):
                        # Complex values - extract magnitude and phase
                        magnitude = np.abs(values)
                        phase = np.angle(values, deg=True)
                    else:
                        # Real values - magnitude only
                        magnitude = np.abs(values)
                        phase = np.zeros_like(values)
                    break
        
        return frequencies, magnitude, phase
    
    @staticmethod
    def export_to_csv(data: Dict, csv_path: str):
        """
        Export parsed data to CSV format
        """
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)