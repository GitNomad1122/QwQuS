"""
RC Filter SimulationDemo with Visualization
"""
import matplotlib.pyplot as plt
import numpy as np
from qwqus.core.simulator import CircuitSimulator
from qwqus.core.netlist import rc_lowpass_netlist, calculate_rc_cutoff


def main():
    print("🚀 Running RC low-pass filter simulation...")
    print("   R = 1 kOhm, C = 100 nF → calculated cutoff frequency: 1.59 kHz\n")
    
    # 1. Create simulator (auto-detect QUCS-S or mock)
    sim = CircuitSimulator(use_mock=False)  # False = try real simulation
    
    #2. Generate netlist
    netlist = rc_lowpass_netlist(r_ohm=1000, c_farad=100e-9)
    
    # 3. Run simulation
    results = sim.simulate(
        netlist,
        analysis_type="ac",
        f_start=10,
        f_stop=100_000
    )
    
    # 4. Visualization
    plt.figure(figsize=(10, 6))
    
    # Amplitude-frequency characteristic
    plt.subplot(2, 1, 1)
    plt.semilogx(results.frequencies, results.magnitude_db, 'b-', linewidth=2)
    plt.axvline(1590, color='r', linestyle='--', alpha=0.7, label='fc = 1.59 kHz (theory)')
    plt.axhline(-3, color='g', linestyle=':', alpha=0.7, label='-3 dB')
    plt.title('RC Low-Pass Filter (R=1 kOhm, C=100 nF)', fontsize=14, fontweight='bold')
    plt.ylabel('Amplitude (dB)')
    plt.grid(True, which='both',ls='--', alpha=0.7)
    plt.legend()
    
    # Phase-frequency characteristic
    if results.phase is not None:
        plt.subplot(2, 1, 2)
        plt.semilogx(results.frequencies, results.phase, 'purple', linewidth=2)
        plt.axvline(1590, color='r', linestyle='--', alpha=0.7)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase (°)')
        plt.grid(True, which='both', ls='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('rc_filter_response.png', dpi=150, bbox_inches='tight')
    print("✅ Chart saved: rc_filter_response.png")
    plt.show()
    
    # 5. Calculated verification
    fc_measured = results.frequencies[np.argmin(np.abs(results.magnitude_db + 3))]
    print(f"\n📊 Analysis Results:")
    print(f"   • Theoretical cutoff frequency: 1.59 kHz")
    print(f"   • Measured cutoff frequency (-3 dB): {fc_measured/1000:.2f} kHz")
    print(f"   • Deviation: {abs(fc_measured - 1590)/1590*100:.1f}%")


if __name__ == "__main__":
    main()
