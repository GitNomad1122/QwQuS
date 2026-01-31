"""
Generator for netlists for typical circuits
"""
from typing import Dict


def rc_lowpass_netlist(r_ohm: float = 1000, c_farad: float = 100e-9) -> str:
    """
    Generates netlist for RC low-pass filter
    
    Circuit:
        Vin ──R──┬── Vout
                 │
                 C
                 │
                GND
    
    Args:
        r_ohm: Resistor value (Ohms)
        c_farad: Capacitor value (Farads)
    
    Returns:
        String with QUCS netlist format
    """
    # Format values in engineering notation
    r_str = format_eng(r_ohm)
    c_str = format_eng(c_farad)
    
    # Standard QUCS format that works with both real and mock simulators
    return f"""V1 in 0 DC 0 AC 1
R1 in out {r_str}
C1 out 0 {c_str}
.control
ac dec 100 1 1MEG
.end
.end
"""


def rc_highpass_netlist(r_ohm: float = 1000, c_farad: float = 100e-9) -> str:
    """Generates netlist for RC high-pass filter"""
    r_str = format_eng(r_ohm)
    c_str = format_eng(c_farad)
    
    return f"""V1 in 0 DC 0 AC 1
C1 in out {c_str}
R1 out 0 {r_str}
.control
ac dec 100 1 1MEG
.end
.end
"""


def opamp_inverting_amplifier(r1_ohm: float = 1000, r2_ohm: float = 10000) -> str:
    """Generates netlist for inverting amplifier on OPAMP"""
    r1_str = format_eng(r1_ohm)
    r2_str = format_eng(r2_ohm)
    
    # For now, simplified version - in real implementation would need proper opamp model
    return f"""Vin in 0 DC 0 AC 1
R1 in inv {r1_str}
R2 inv out {r2_str}
Eout out 0 in 0 0  ; Voltage controlled voltage source as ideal opamp
.control
ac dec 100 1 1MEG
.end
.end
"""


def format_eng(value: float) -> str:
    """
    Format value in engineering notation (k, m, u, n, etc.)
    """
    if value >= 1e9:
        return f"{value/1e9:g}G"
    elif value >= 1e6:
        return f"{value/1e6:g}M"
    elif value >= 1e3:
        return f"{value/1e3:g}k"
    elif value >= 1:
        return f"{value:g}"
    elif value >= 1e-3:
        return f"{value/1e-3:g}m"
    elif value >= 1e-6:
        return f"{value/1e-6:g}u"
    elif value >= 1e-9:
        return f"{value/1e-9:g}n"
    elif value >= 1e-12:
        return f"{value/1e-12:g}p"
    else:
        return f"{value:g}"


def calculate_rc_cutoff(r_ohm: float, c_farad: float) -> float:
    """
    Calculate cutoff frequency for RC circuit: fc = 1/(2πRC)
    """
    return 1 / (2 * 3.14159 * r_ohm * c_farad)


# Export
__all__ = ["rc_lowpass_netlist", "rc_highpass_netlist", "opamp_inverting_amplifier", "calculate_rc_cutoff"]