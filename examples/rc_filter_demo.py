"""
RC Filter Demo for QwQuS
Demonstrates basic circuit simulation with visualization
"""
import sys
import os

# Add the qwqus package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qwqus.core.simulator import simulate_circuit
from qwqus.core.netlist import rc_lowpass_netlist, calculate_rc_cutoff
import matplotlib.pyplot as plt
import numpy as np


def run_rc_filter_demo():
    """
    Run RC low-pass filter simulation and visualization
    """
    print("🔧 Initializing QwQuS Circuit Simulator...")
    
    print("\n📝 Creating RC low-pass filter netlist...")
    # Create a simple RC low-pass filter (R=1kΩ, C=100nF)
    R_VALUE = 1000  # 1k Ohms
    C_VALUE = 100e-9  # 100 nF
    
    netlist = rc_lowpass_netlist(r_ohm=R_VALUE, c_farad=C_VALUE)
    print("Generated netlist:")
    print(netlist)
    
    # Calculate theoretical cutoff
    theoretical_fc = calculate_rc_cutoff(R_VALUE, C_VALUE)
    print(f"\n🔍 Theoretical cutoff frequency: {theoretical_fc:.2f} Hz")
    
    print("\n🚀 Running AC simulation...")
    # Run the simulation
    results = simulate_circuit(
        netlist=netlist,
        analysis_type='ac',
        f_start=1,      # 1 Hz
        f_stop=1e6,     # 1 MHz
        output_vars=['frequency', 'output_voltage']  # Looking for frequency and output voltage
    )
    
    print(f"\n✅ Simulation completed: {results['message']}")
    print(f"Analysis type: {results['analysis_type']}")
    
    # Print the data keys available
    print(f"Available data keys: {list(results['data'].keys())}")
    
    # Visualize the results
    print("\n📊 Plotting results...")
    try:
        # Get the data
        data = results['data']
        
        # Extract frequency and magnitude data
        if 'frequency' in data and ('magnitude' in data or 'output_voltage' in data):
            frequencies = np.array(data['frequency'])
            
            # Use output_voltage if available, otherwise use magnitude
            if 'output_voltage' in data:
                magnitude = np.array(data['output_voltage'])
            else:
                magnitude = np.array(data['magnitude'])
            
            # Create magnitude plot in dB
            magnitude_db = 20 * np.log10(magnitude)
            
            # Create plots
            plt.figure(figsize=(12, 8))
            
            # Magnitude plot
            plt.subplot(2, 1, 1)
            plt.semilogx(frequencies, magnitude_db)
            plt.title(f'RC Low-Pass Filter Response\nR={R_VALUE/1000:g}kΩ, C={C_VALUE*1e9:g}nF, fc≈{theoretical_fc:.1f}Hz')
            plt.ylabel('Magnitude (dB)')
            plt.grid(True, which="both", ls="-", alpha=0.3)
            
            # Add cutoff frequency line
            plt.axvline(x=theoretical_fc, color='red', linestyle='--', alpha=0.7, label=f'Fc = {theoretical_fc:.1f} Hz')
            plt.legend()
            
            # Phase plot if available
            if 'phase' in data:
                phase = np.array(data['phase'])
                plt.subplot(2, 1, 2)
                plt.semilogx(frequencies, np.degrees(phase))
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Phase (degrees)')
                plt.grid(True, which="both", ls="-", alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            # Print some key values
            print(f"\n📈 Key Results:")
            print(f"  - At low frequencies (< {theoretical_fc/10:.0f} Hz): ~0 dB (passband)")
            print(f"  - At cutoff frequency ({theoretical_fc:.1f} Hz): approximately -3 dB")
            print(f"  - At high frequencies (> {theoretical_fc*10:.0f} Hz): decreasing at -20 dB/decade (stopband)")
        else:
            print("⚠️ Could not find appropriate data for plotting")
            print("Available data keys:", list(data.keys()))
    
    except Exception as e:
        print(f"⚠️ Error plotting results: {e}")
        # Try to show raw data
        if 'data' in results:
            print("Raw data keys:", list(results['data'].keys()))


def explain_rc_basics():
    """
    Explain the basics of RC low-pass filters
    """
    print("\n📖 RC Low-Pass Filter Basics:")
    print("- Consists of a resistor (R) and capacitor (C) in series")
    print("- Allows low frequencies to pass through while attenuating high frequencies")
    print("- Cutoff frequency: fc = 1/(2πRC)")
    print("- At fc, the output is reduced by 3 dB (~70.7% of input)")
    print("- Roll-off rate: -20 dB per decade (-6 dB per octave)")


if __name__ == "__main__":
    print("🧪 Running RC Filter Demo for QwQuS")
    print("="*60)
    
    # Explain basics
    explain_rc_basics()
    
    # Run the demo
    run_rc_filter_demo()
    
    print("\n✨ RC Filter Demo completed!")
    print("💡 Next: Try changing R and C values to see how they affect the filter response")