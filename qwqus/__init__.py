"""
QwQuS - AI-Powered Circuit Simulation with Qwen-Agent and QUCS-S
"""
from .core.simulator import QucsSimulator, simulate_circuit
from .core.netlist import (
    generate_netlist,
    rc_lowpass_netlist,
    rc_highpass_netlist,
    voltage_divider_netlist,
    lc_tank_netlist,
    calculate_rc_cutoff,
    calculate_lc_resonance
)

__version__ = "0.1.0"
__author__ = "GitNomad1122"
__license__ = "MIT"

__all__ = [
    # Core simulator
    'QucsSimulator',
    'simulate_circuit',
    
    # Netlist generation
    'generate_netlist',
    'rc_lowpass_netlist',
    'rc_highpass_netlist',
    'voltage_divider_netlist',
    'lc_tank_netlist',
    'calculate_rc_cutoff',
    'calculate_lc_resonance',
]