"""
Core simulator module for QwQuS
Contains both real QUCS integration and mock simulator for testing
"""
import os
import subprocess
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union
from .netlist import generate_netlist


class QucsSimulator:
    """
    Main simulator class that handles communication with QUCSator
    Falls back to mock simulator if QUCSator is not available
    """
    
    def __init__(self):
        self.has_qucsator = self._check_qucsator()
        if self.has_qucsator:
            print("✅ QUCSator found and available for simulations")
        else:
            print("⚠️ QUCSator not found or not working properly. Using mock simulator for demonstrations.")
            print("💡 Tip: Make sure QUCS-S is properly installed and qucsator is in your PATH")
    
    def _check_qucsator(self) -> bool:
        """
        Check if qucsator is available in the system
        """
        try:
            import shutil
            # Check for all possible qucsator executable names
            possible_names = ['qucsator', 'qucsator.exe', 'qucsator_rf', 'qucsator_rf.exe']
            for name in possible_names:
                if shutil.which(name):
                    # Test if the executable actually works
                    try:
                        result = subprocess.run([name, '--version'], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            return True
                    except:
                        continue
            return False
        except:
            # Fallback check for different platforms
            possible_names = ['qucsator', 'qucsator.exe', 'qucsator_rf', 'qucsator_rf.exe']
            for name in possible_names:
                try:
                    if os.name == 'nt':  # Windows
                        result = subprocess.run(['where', name], capture_output=True, text=True, timeout=10)
                    else:  # Unix-like
                        result = subprocess.run(['which', name], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        # Also test if it runs properly
                        try:
                            test_result = subprocess.run([name, '--version'], 
                                                       capture_output=True, text=True, timeout=10)
                            if test_result.returncode == 0:
                                return True
                        except:
                            continue
                except:
                    continue
            return False
    
    def simulate(self, netlist: str, analysis_type: str = 'ac', 
                 f_start: float = 1, f_stop: float = 1e6, 
                 output_vars: Optional[List[str]] = None) -> Dict:
        """
        Simulate a circuit using QUCSator if available, otherwise use mock
        """
        if self.has_qucsator:
            result = self._simulate_real(netlist, analysis_type, f_start, f_stop, output_vars)
            # If real simulation fails, fall back to mock
            if 'error' in result:
                print(f"⚠️ Real simulation failed: {result['error']}")
                print("🔄 Falling back to mock simulator...")
                return self._simulate_mock(netlist, analysis_type, f_start, f_stop, output_vars)
            return result
        else:
            return self._simulate_mock(netlist, analysis_type, f_start, f_stop, output_vars)
    
    def _simulate_real(self, netlist: str, analysis_type: str, f_start: float, 
                       f_stop: float, output_vars: Optional[List[str]]) -> Dict:
        """
        Perform real simulation using QUCSator
        """
        # Find the correct qucsator executable name
        qucsator_cmd = self._find_qucsator_executable()
        if not qucsator_cmd:
            return {'error': 'QUCSator executable not found'}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write netlist to temporary file
            netlist_path = os.path.join(temp_dir, 'circuit.net')
            with open(netlist_path, 'w', encoding='utf-8') as f:
                f.write(netlist)
            
            # Run QUCS simulation
            try:
                result = subprocess.run([
                    qucsator_cmd, '-i', netlist_path, '-o', os.path.join(temp_dir, 'output.dat')
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    raise Exception(f"Simulation failed: {result.stderr}")
                
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
                    'message': 'Real simulation completed successfully'
                }
                
            except subprocess.TimeoutExpired:
                return {
                    'error': 'Simulation timed out'
                }
            except Exception as e:
                return {
                    'error': f'Real simulation error: {str(e)}'
                }
    
    def _find_qucsator_executable(self) -> Optional[str]:
        """
        Find the correct QUCSator executable in the system
        """
        possible_names = ['qucsator', 'qucsator.exe', 'qucsator_rf', 'qucsator_rf.exe']
        
        for name in possible_names:
            try:
                import shutil
                if shutil.which(name):
                    return name
            except:
                # Fallback to subprocess
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
    
    def _simulate_mock(self, netlist: str, analysis_type: str, f_start: float, 
                       f_stop: float, output_vars: Optional[List[str]]) -> Dict:
        """
        Mock simulation for demonstration when QUCSator is not available
        Generates realistic data for common circuit types
        """
        # Detect circuit type from netlist to generate appropriate mock data
        if 'R1' in netlist and 'C1' in netlist:
            # Likely RC circuit
            return self._mock_rc_simulation(analysis_type, f_start, f_stop)
        elif 'L1' in netlist and 'C1' in netlist:
            # Likely LC circuit
            return self._mock_lc_simulation(analysis_type, f_start, f_stop)
        else:
            # Generic response
            return self._mock_generic_simulation(analysis_type, f_start, f_stop)
    
    def _mock_rc_simulation(self, analysis_type: str, f_start: float, f_stop: float) -> Dict:
        """
        Generate mock data for RC circuit simulation
        """
        frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), num=100)
        
        # Calculate for RC low-pass (assuming R=1k, C=1uF, fc ~ 159 Hz)
        R = 1000  # 1kOhm
        C = 1e-6  # 1uF
        fc = 1 / (2 * np.pi * R * C)  # ~159 Hz
        
        # Calculate magnitude response (|H(jω)| = 1/sqrt(1 + (f/fc)^2))
        magnitude = 1 / np.sqrt(1 + (frequencies / fc)**2)
        
        # Calculate phase response (φ = -arctan(f/fc))
        phase = -np.arctan(frequencies / fc)
        
        return {
            'success': True,
            'analysis_type': analysis_type,
            'data': {
                'frequency': frequencies.tolist(),
                'magnitude': magnitude.tolist(),
                'phase': phase.tolist(),
                'output_voltage': magnitude.tolist()  # Simulated output
            },
            'message': 'Mock simulation completed (RC circuit)'
        }
    
    def _mock_lc_simulation(self, analysis_type: str, f_start: float, f_stop: float) -> Dict:
        """
        Generate mock data for LC circuit simulation
        """
        frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), num=100)
        
        # Calculate for LC resonant circuit (assuming L=1mH, C=1uF, f_resonance ~ 5.03 kHz)
        L = 1e-3  # 1mH
        C = 1e-6  # 1uF
        f_res = 1 / (2 * np.pi * np.sqrt(L * C))  # ~5.03 kHz
        
        # Impedance varies around resonance
        Z = np.abs(2 * np.pi * frequencies * L - 1 / (2 * np.pi * frequencies * C))
        
        # Normalize to reasonable values
        impedance = 1 / (1 + ((frequencies - f_res) / (f_res * 0.1))**2)  # Peak at resonance
        
        return {
            'success': True,
            'analysis_type': analysis_type,
            'data': {
                'frequency': frequencies.tolist(),
                'impedance': impedance.tolist(),
                'voltage': impedance.tolist()
            },
            'message': 'Mock simulation completed (LC circuit)'
        }
    
    def _mock_generic_simulation(self, analysis_type: str, f_start: float, f_stop: float) -> Dict:
        """
        Generate generic mock simulation data
        """
        frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), num=100)
        magnitude = np.ones_like(frequencies) * 0.707  # -3dB typical
        
        return {
            'success': True,
            'analysis_type': analysis_type,
            'data': {
                'frequency': frequencies.tolist(),
                'magnitude': magnitude.tolist(),
                'output': magnitude.tolist()
            },
            'message': 'Mock simulation completed (generic circuit)'
        }
    
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


def simulate_circuit(netlist: str, analysis_type: str = 'ac', f_start: float = 1, 
                     f_stop: float = 1e6, output_vars: Optional[List[str]] = None) -> Dict:
    """
    Convenience function to simulate a circuit
    """
    simulator = QucsSimulator()
    return simulator.simulate(netlist, analysis_type, f_start, f_stop, output_vars)


if __name__ == "__main__":
    # Example usage
    simulator = QucsSimulator()
    
    # Simple RC circuit netlist example
    rc_netlist = """V1 in 0 DC 0 AC 1
R1 in out 1k
C1 out 0 1uF
.control
ac dec 10 1 1MEG
.end
.end
"""
    
    print(f"QUCSator available: {simulator.has_qucsator}")
    result = simulator.simulate(rc_netlist, 'ac', 1, 1e6, ['frequency', 'out'])
    print(result)