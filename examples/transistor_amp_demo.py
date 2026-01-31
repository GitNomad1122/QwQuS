"""
Transistor Amplifier Demo for QwQuS
Demonstrates bipolar junction transistor amplifier simulation
"""
import sys
import os

# Add the qwqus package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qwqus.tools.qucs_simulator import QucsSimulator
from qwqus.utils.netlist_templates import NetlistTemplates
import matplotlib.pyplot as plt
import numpy as np


def run_transistor_amplifier_demo():
    """
    Run common emitter transistor amplifier simulation and visualization
    """
    print("🔧 Initializing QUCS Simulator...")
    simulator = QucsSimulator()
    
    print("\n📝 Creating Common Emitter Amplifier netlist...")
    # Create a simple common emitter amplifier
    amp_netlist = NetlistTemplates.common_em_amplifier(
        beta="100",      # Transistor beta (current gain)
        Rc="2k",         # Collector resistor
        Re="1k",         # Emitter resistor
        R1="10k",        # Base bias resistor 1
        R2="10k",        # Base bias resistor 2
        Vcc="12",        # Supply voltage
        Vin="0.01"       # Small AC input signal
    )
    print("Generated netlist:")
    print(amp_netlist)
    
    print("\n🚀 Running AC simulation...")
    # Run the simulation
    result = simulator._run(
        netlist=amp_netlist,
        analysis_type='ac',
        output_vars=['frequency', 'collector']  # Looking for frequency and collector voltage
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
            elif 'collector' in key.lower() or 'v(' in key.lower():
                output_data = values
        
        if freq_data is not None and output_data is not None:
            # Create magnitude plot
            plt.figure(figsize=(12, 8))
            
            # Magnitude plot
            plt.subplot(2, 1, 1)
            if all(isinstance(v, complex) for v in output_data):
                magnitude_db = 20 * np.log10(np.abs(output_data))
                plt.loglog(freq_data, magnitude_db)
                plt.ylabel('Magnitude (dB)')
            else:
                plt.loglog(freq_data, np.abs(output_data))
                plt.ylabel('Magnitude')
            
            plt.title('Common Emitter Amplifier Frequency Response')
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
            QucsSimulator.plot_results(data, result['analysis_type'], "Transistor Amplifier Response")
    
    except Exception as e:
        print(f"⚠️ Error plotting results: {e}")
        # Fallback to general plotting
        QucsSimulator.plot_results(result['data'], result['analysis_type'], "Transistor Amplifier Response")


def explain_amplifier_basics():
    """
    Explain the basics of common emitter amplifiers
    """
    print("\n📖 Common Emitter Amplifier Basics:")
    print("- Uses bipolar junction transistor (BJT)")
    print("- Provides voltage and current gain")
    print("- Inverts the input signal (180° phase shift)")
    print("- Input applied to base, output taken from collector")
    print("- Emitter is common to both input and output (hence the name)")
    print("- Bias resistors (R1, R2) set the DC operating point")
    print("- Collector resistor (Rc) converts collector current to voltage")


if __name__ == "__main__":
    print("🧪 Running Transistor Amplifier Demo for QwQuS")
    print("="*50)
    
    # Explain amplifier basics
    explain_amplifier_basics()
    
    # Run the demo
    run_transistor_amplifier_demo()
    
    print("\n✨ Transistor Amplifier Demo completed!")