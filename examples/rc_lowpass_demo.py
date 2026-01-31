"""
RC Low-Pass Filter Demo for QwQuS
Demonstrates basic functionality of the QUCS integration with Qwen-Agent
"""
import sys
import os

# Add the qwqus package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qwqus.tools.qucs_simulator import QucsSimulator
from qwqus.utils.netlist_templates import NetlistTemplates
import matplotlib.pyplot as plt
import numpy as np


def run_rc_lowpass_demo():
    """
    Run RC low-pass filter simulation and visualization
    """
    print("🔧 Initializing QUCS Simulator...")
    simulator = QucsSimulator()
    
    print("\n📝 Creating RC low-pass filter netlist...")
    # Create a simple RC low-pass filter
    rc_netlist = NetlistTemplates.rc_low_pass(R_value="1k", C_value="1uF", Vin="1")
    print("Generated netlist:")
    print(rc_netlist)
    
    print("\n🚀 Running AC simulation...")
    # Run the simulation
    result = simulator._run(
        netlist=rc_netlist,
        analysis_type='ac',
        output_vars=['frequency', 'out']  # Looking for frequency and output voltage
    )
    
    if 'error' in result:
        print(f"❌ Simulation failed: {result['error']}")
        return
    
    print(f"\n✅ Simulation completed: {result['message']}")
    print(f"Analysis type: {result['analysis_type']}")
    
    # Print the data keys available
    print(f"Available data keys: {list(result['data'].keys())}")
    
    # Visualize the results
    print("\n📊 Plotting results...")
    try:
        # Get the data
        data = result['data']
        
        # Find frequency and output data
        freq_data = None
        output_data = None
        
        for key, values in data.items():
            if 'freq' in key.lower():
                freq_data = values
            elif 'out' in key.lower() or 'v(' in key.lower():
                output_data = values
        
        if freq_data is not None and output_data is not None:
            # Create magnitude plot
            plt.figure(figsize=(12, 8))
            
            # Magnitude plot
            plt.subplot(2, 1, 1)
            if all(isinstance(v, complex) for v in output_data):
                magnitude_db = 20 * np.log10(np.abs(output_data))
                plt.semilogx(freq_data, magnitude_db)
                plt.ylabel('Magnitude (dB)')
            else:
                plt.semilogx(freq_data, np.abs(output_data))
                plt.ylabel('Magnitude')
            
            plt.title('RC Low-Pass Filter Frequency Response')
            plt.grid(True)
            
            # Phase plot if available
            if all(isinstance(v, complex) for v in output_data):
                plt.subplot(2, 1, 2)
                phase_deg = np.angle(output_data, deg=True)
                plt.semilogx(freq_data, phase_deg)
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Phase (degrees)')
                plt.grid(True)
            
            plt.tight_layout()
            plt.show()
        else:
            print("⚠️ Could not find appropriate data for plotting")
            # Fallback: use the general plotting function
            QucsSimulator.plot_results(data, result['analysis_type'], "RC Low-Pass Filter Response")
    
    except Exception as e:
        print(f"⚠️ Error plotting results: {e}")
        # Fallback to general plotting
        QucsSimulator.plot_results(result['data'], result['analysis_type'], "RC Low-Pass Filter Response")


def calculate_theoretical_cutoff(R_value: float, C_value: float) -> float:
    """
    Calculate theoretical cutoff frequency for RC circuit
    fc = 1 / (2 * pi * R * C)
    """
    return 1 / (2 * np.pi * R_value * C_value)


if __name__ == "__main__":
    print("🧪 Running RC Low-Pass Filter Demo for QwQuS")
    print("="*50)
    
    # Show theoretical calculation
    R_val = 1000  # 1k Ohm
    C_val = 1e-6  # 1uF
    theoretical_fc = calculate_theoretical_cutoff(R_val, C_val)
    print(f"Theoretical cutoff frequency: {theoretical_fc:.2f} Hz")
    
    # Run the demo
    run_rc_lowpass_demo()
    
    print("\n✨ RC Low-Pass Demo completed!")