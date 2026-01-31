"""
QwQuS - AI-Powered Circuit Simulation with Qwen-Agent and QUCS-S
"""
from .core.simulator import CircuitSimulator, SimulationResult
from .core.netlist import (
    rc_lowpass_netlist,
    rc_highpass_netlist,
    opamp_inverting_amplifier,
    calculate_rc_cutoff
)

__version__ = "0.1.0"
__author__ = "GitNomad1122"
__license__ = "MIT"

__all__ = [
    # Core simulator
    'CircuitSimulator',
    'SimulationResult',
    
    # Netlist generation
    'rc_lowpass_netlist',
    'rc_highpass_netlist',
    'opamp_inverting_amplifier',
    'calculate_rc_cutoff',
]