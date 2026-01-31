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
        # Check if qucsator is available
        qucsator_cmd = self._find_qucsator()
        if not qucsator_cmd:
            return {
                'error': 'QUCSator not found in PATH. Please install QUCS-S and ensure qucsator is in PATH. '
                         'Download from: https://github.com/ra3xdh/qucs_s/releases. '
                         'Current supported executable names: qucsator, qucsator.exe, qucsator_rf, qucsator_rf.exe'
            }
        
        # Create temporary directory for simulation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write netlist to temporary file
            netlist_path = os.path.join(temp_dir, 'circuit.net')
            with open(netlist_path, 'w', encoding='utf-8') as f:
                f.write(netlist)
            
            # Run QUCS simulation
            try:
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
        # Try common locations for qucsator - including RF version
        possible_names = ['qucsator', 'qucsator.exe', 'qucsator_rf', 'qucsator_rf.exe']
        
        for name in possible_names:
            # Check if it's in PATH using shutil.which for better cross-platform support
            try:
                import shutil
                cmd_path = shutil.which(name)
                if cmd_path:
                    return name
            except:
                # Fallback to subprocess for systems where shutil.which doesn't work
                try:
                    if os.name == 'nt':  # Windows
                        result = subprocess.run(['where', name], capture_output=True, text=True)
                    else:  # Unix-like
                        result = subprocess.run(['which', name], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        return name
                except:
                    continue
        
        return None

    def _parse_output(self, dat_file: str) -> Dict:
        """
        Parse QUCS output .dat file
        """
        if not os.path.exists(dat_file):
            return {}
        
        data = {}
        try:
            with open(dat_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(dat_file, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        
        current_var = None
        current_values = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Symbol'):
                # Extract variable name
                parts = line.split()
                if len(parts) >= 2:
                    # Store previous variable if exists
                    if current_var and current_values:
                        data[current_var] = current_values
                    
                    # Start new variable
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
                # Check if values are numeric
                numeric_values = []
                for val in values:
                    if isinstance(val, (int, float, complex)):
                        numeric_values.append(val)
                    elif isinstance(val, str):
                        try:
                            numeric_values.append(float(val))
                        except ValueError:
                            continue
                
                if not numeric_values:
                    continue
                    
                # If first column looks like frequency/time, use it as x-axis
                if 'freq' in key.lower() or 'time' in key.lower() or 'indep' in key.lower():
                    x_vals = numeric_values
                    # Find corresponding dependent variable
                    for dep_key, dep_values in data.items():
                        if dep_key != key and isinstance(dep_values, list):
                            y_vals = []
                            for val in dep_values:
                                if isinstance(val, (int, float, complex)):
                                    y_vals.append(val)
                                elif isinstance(val, str):
                                    try:
                                        y_vals.append(float(val))
                                    except ValueError:
                                        continue
                            
                            if len(y_vals) > 0:
                                plt.plot(x_vals[:len(y_vals)], y_vals, label=dep_key, marker='o')
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
                        indep_vals = []
                        for val in data[indep_key]:
                            if isinstance(val, (int, float)):
                                indep_vals.append(val)
                            elif isinstance(val, str):
                                try:
                                    indep_vals.append(float(val))
                                except ValueError:
                                    continue
                        
                        y_vals = []
                        for val in values:
                            if isinstance(val, (int, float, complex)):
                                y_vals.append(val)
                            elif isinstance(val, str):
                                try:
                                    y_vals.append(float(val))
                                except ValueError:
                                    continue
                        
                        if len(indep_vals) == len(y_vals):
                            plt.plot(indep_vals, y_vals, label=key, marker='o')
                        else:
                            x_vals = list(range(len(y_vals)))
                            plt.plot(x_vals, y_vals, label=key, marker='o')
                    else:
                        x_vals = list(range(len(numeric_values)))
                        plt.plot(x_vals, numeric_values, label=key, marker='o')
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