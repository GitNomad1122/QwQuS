"""
Custom QUCS Simulator Tool for Qwen-Agent
Provides integration between Qwen-Agent and QUCS circuit simulator
"""
import os
import subprocess
import tempfile
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union
from qwen_agent.tools import BaseTool


class QucsSimulator(BaseTool):
    """
    A tool that enables Qwen-Agent to interact with QUCS circuit simulator
    """
    def __init__(self):
        super().__init__()
        self.name = 'qucs_simulator'
        self.description = 'Run circuit simulations using QUCS simulator'
        self.parameters = {
            'type': 'object',
            'properties': {
                'netlist': {
                    'type': 'string',
                    'description': 'QUCS netlist to simulate'
                },
                'analysis_type': {
                    'type': 'string',
                    'enum': ['ac', 'dc', 'transient', 'custom'],
                    'description': 'Type of analysis to perform'
                },
                'output_vars': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Variables to extract from simulation'
                }
            },
            'required': ['netlist']
        }

    def _run(self, netlist: str, analysis_type: str = 'ac', output_vars: Optional[List[str]] = None) -> Dict:
        """
        Run circuit simulation using QUCS
        """
        # Create temporary directory for simulation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write netlist to temporary file
            netlist_path = os.path.join(temp_dir, 'circuit.net')
            with open(netlist_path, 'w') as f:
                f.write(netlist)
            
            # Run QUCS simulation
            try:
                # Find qucsator executable
                qucsator_cmd = self._find_qucsator()
                if not qucsator_cmd:
                    return {
                        'error': 'QUCSator not found in PATH. Please install QUCS-S and ensure qucsator is in PATH.'
                    }
                
                # Execute simulation
                result = subprocess.run([
                    qucsator_cmd, '-i', netlist_path, '-o', os.path.join(temp_dir, 'output.dat')
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    return {
                        'error': f'Simulation failed: {result.stderr}'
                    }
                
                # Parse output data
                output_data = self._parse_output(os.path.join(temp_dir, 'output.dat'))
                
                # Filter output variables if specified
                if output_vars:
                    filtered_data = {}
                    for var in output_vars:
                        if var in output_data:
                            filtered_data[var] = output_data[var]
                        else:
                            # Try to find partial matches
                            for key in output_data:
                                if var.lower() in key.lower():
                                    filtered_data[key] = output_data[key]
                                    break
                    output_data = filtered_data
                
                return {
                    'success': True,
                    'analysis_type': analysis_type,
                    'data': output_data,
                    'message': 'Simulation completed successfully'
                }
                
            except subprocess.TimeoutExpired:
                return {
                    'error': 'Simulation timed out'
                }
            except Exception as e:
                return {
                    'error': f'Simulation error: {str(e)}'
                }

    def _find_qucsator(self) -> Optional[str]:
        """
        Find QUCSator executable in system PATH
        """
        # Try common locations for qucsator
        possible_names = ['qucsator', 'qucsator.exe']
        
        for name in possible_names:
            # Check if it's in PATH
            result = subprocess.run(['where', name], capture_output=True, text=True)
            if result.returncode == 0:
                return name
        
        # On Unix-like systems, also try 'which'
        if os.name != 'nt':
            for name in possible_names:
                result = subprocess.run(['which', name], capture_output=True, text=True)
                if result.returncode == 0:
                    return name
        
        return None

    def _parse_output(self, dat_file: str) -> Dict:
        """
        Parse QUCS output .dat file
        """
        if not os.path.exists(dat_file):
            return {}
        
        data = {}
        with open(dat_file, 'r') as f:
            lines = f.readlines()
        
        current_var = None
        current_values = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Symbol'):
                # Extract variable name
                parts = line.split()
                if len(parts) >= 2:
                    current_var = parts[1].strip()
                    current_values = []
            elif line.startswith('Values'):
                continue  # Skip header line
            elif line.startswith('#') or line == '':
                # Handle variable boundary or comments
                if current_var and current_values:
                    data[current_var] = current_values
                    current_var = None
                    current_values = []
            else:
                # Parse numeric values
                try:
                    # Handle complex numbers and regular numbers
                    if ',' in line:
                        # Complex number format: real,imag
                        real, imag = map(float, line.split(','))
                        current_values.append(complex(real, imag))
                    else:
                        # Regular number
                        current_values.append(float(line))
                except ValueError:
                    # Skip lines that aren't numeric
                    continue
        
        # Don't forget the last variable
        if current_var and current_values:
            data[current_var] = current_values
        
        return data

    @staticmethod
    def plot_results(data: Dict, analysis_type: str = 'ac', title: str = "Simulation Results"):
        """
        Plot simulation results using matplotlib
        """
        if not data:
            print("No data to plot")
            return
        
        plt.figure(figsize=(10, 6))
        
        plotted = False
        for key, values in data.items():
            if isinstance(values, list) and len(values) > 0:
                x_vals = list(range(len(values)))  # Use index as x-axis if no frequency/time data
                y_vals = values
                
                # If first column looks like frequency/time, use it as x-axis
                if 'freq' in key.lower() or 'time' in key.lower() or 'indep' in key.lower():
                    x_vals = values
                    # Find corresponding dependent variable
                    for dep_key, dep_values in data.items():
                        if dep_key != key and isinstance(dep_values, list):
                            plt.plot(x_vals[:len(dep_values)], dep_values, label=dep_key, marker='o')
                            plotted = True
                            break
                else:
                    # If we have independent variable, use it for x-axis
                    indep_key = None
                    for k in data.keys():
                        if 'freq' in k.lower() or 'time' in k.lower() or 'indep' in k.lower():
                            indep_key = k
                            break
                    
                    if indep_key:
                        indep_vals = data[indep_key][:len(values)]
                        plt.plot(indep_vals, values, label=key, marker='o')
                    else:
                        plt.plot(x_vals, values, label=key, marker='o')
                    plotted = True
        
        if plotted:
            plt.title(title)
            plt.xlabel('Frequency (Hz)' if 'ac' in analysis_type.lower() else 'Time (s)')
            plt.ylabel('Magnitude')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print("No suitable data to plot")


if __name__ == "__main__":
    # Example usage
    simulator = QucsSimulator()
    
    # Simple RC circuit netlist example
    rc_netlist = """* RC Low Pass Filter
V1 in 0 DC 0 AC 1
R1 in out 1k
C1 out 0 1uF
.control
ac dec 10 1 1MEG
.end
.end
"""
    
    result = simulator._run(rc_netlist, 'ac', ['frequency', 'out'])
    print(result)