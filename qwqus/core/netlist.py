"""
Netlist generator for QwQuS
Provides functions to generate QUCS-compatible netlists for common circuits
NOTE: The format here is designed to work with both mock simulator and real QUCSator
when properly configured. For QUCSator to work, proper component syntax is required.
"""
from typing import Dict, Optional


def generate_netlist(circuit_type: str, **kwargs) -> str:
    """
    Generate a netlist based on circuit type and parameters
    """
    if circuit_type.lower() == 'rc_lowpass':
        return rc_lowpass_netlist(
            r_ohm=kwargs.get('r_ohm', 1000),
            c_farad=kwargs.get('c_farad', 1e-6),
            vin=kwargs.get('vin', 1)
        )
    elif circuit_type.lower() == 'rc_highpass':
        return rc_highpass_netlist(
            r_ohm=kwargs.get('r_ohm', 1000),
            c_farad=kwargs.get('c_farad', 1e-6),
            vin=kwargs.get('vin', 1)
        )
    elif circuit_type.lower() == 'voltage_divider':
        return voltage_divider_netlist(
            r1_ohm=kwargs.get('r1_ohm', 1000),
            r2_ohm=kwargs.get('r2_ohm', 1000),
            vin=kwargs.get('vin', 1)
        )
    elif circuit_type.lower() == 'lc_tank':
        return lc_tank_netlist(
            l_henry=kwargs.get('l_henry', 1e-3),
            c_farad=kwargs.get('c_farad', 1e-6)
        )
    else:
        raise ValueError(f"Unknown circuit type: {circuit_type}")


def rc_lowpass_netlist(r_ohm: float = 1000, c_farad: float = 1e-6, vin: float = 1) -> str:
    """
    Generate netlist for RC low-pass filter
    Calculates cutoff frequency: fc = 1/(2πRC)
    """
    r_str = format_si_prefix(r_ohm, '')
    c_str = format_si_prefix(c_farad, '')
    
    # Calculate cutoff frequency
    fc = 1/(2*3.14159*r_ohm*c_farad)
    
    # Standard SPICE format that works with simulators
    netlist = f"""V1 in 0 DC 0 AC {vin}
R1 in out {r_str}
C1 out 0 {c_str}
.control
ac dec 10 1 1MEG
print ac v(out)
.end
.end
"""
    return netlist


def rc_highpass_netlist(r_ohm: float = 1000, c_farad: float = 1e-6, vin: float = 1) -> str:
    """
    Generate netlist for RC high-pass filter
    Calculates cutoff frequency: fc = 1/(2πRC)
    """
    r_str = format_si_prefix(r_ohm, '')
    c_str = format_si_prefix(c_farad, '')
    
    # Calculate cutoff frequency
    fc = 1/(2*3.14159*r_ohm*c_farad)
    
    netlist = f"""V1 in 0 DC 0 AC {vin}
C1 in out {c_str}
R1 out 0 {r_str}
.control
ac dec 10 1 1MEG
print ac v(out)
.end
.end
"""
    return netlist


def voltage_divider_netlist(r1_ohm: float = 1000, r2_ohm: float = 1000, vin: float = 1) -> str:
    """
    Generate netlist for voltage divider
    Output voltage: vout = vin * r2/(r1+r2)
    """
    r1_str = format_si_prefix(r1_ohm, '')
    r2_str = format_si_prefix(r2_ohm, '')
    
    expected_vout = vin * r2_ohm / (r1_ohm + r2_ohm)
    
    netlist = f"""V1 in 0 DC {vin}
R1 in mid {r1_str}
R2 mid 0 {r2_str}
.control
dc V1 0 5 0.1
print dc v(mid)
.end
.end
"""
    return netlist


def lc_tank_netlist(l_henry: float = 1e-3, c_farad: float = 1e-6) -> str:
    """
    Generate netlist for LC tank circuit
    Resonant frequency: fr = 1/(2π√LC)
    """
    l_str = format_si_prefix(l_henry, '')
    c_str = format_si_prefix(c_farad, '')
    
    resonant_freq = 1 / (2 * 3.14159 * (l_henry * c_farad) ** 0.5)
    
    netlist = f"""I1 0 node1 DC 0 AC 1mA
R1 node1 0 1Meg
L1 node1 node2 {l_str}
C1 node2 0 {c_str}
.control
ac dec 10 1k 100MEG
print ac v(node2)
.end
.end
"""
    return netlist


def format_si_prefix(value: float, unit: str) -> str:
    """
    Format a value with appropriate SI prefix (k, m, u, n, p, etc.)
    """
    abs_val = abs(value)
    
    if abs_val >= 1e9:
        return f"{value/1e9:g}{unit}G"
    elif abs_val >= 1e6:
        return f"{value/1e6:g}{unit}M"
    elif abs_val >= 1e3:
        return f"{value/1e3:g}{unit}k"
    elif abs_val >= 1:
        return f"{value:g}{unit}"
    elif abs_val >= 1e-3:
        return f"{value/1e-3:g}{unit}m"
    elif abs_val >= 1e-6:
        return f"{value/1e-6:g}{unit}u"
    elif abs_val >= 1e-9:
        return f"{value/1e-9:g}{unit}n"
    elif abs_val >= 1e-12:
        return f"{value/1e-12:g}{unit}p"
    else:
        return f"{value:g}{unit}"


def calculate_rc_cutoff(r_ohm: float, c_farad: float) -> float:
    """
    Calculate cutoff frequency for RC circuit: fc = 1/(2πRC)
    """
    return 1 / (2 * 3.14159 * r_ohm * c_farad)


def calculate_lc_resonance(l_henry: float, c_farad: float) -> float:
    """
    Calculate resonant frequency for LC circuit: fr = 1/(2π√LC)
    """
    return 1 / (2 * 3.14159 * (l_henry * c_farad) ** 0.5)


if __name__ == "__main__":
    # Test the netlist generators
    print("RC Low-Pass Filter (1kΩ, 1µF):")
    print(rc_lowpass_netlist())
    print("\nExpected cutoff:", calculate_rc_cutoff(1000, 1e-6), "Hz")
    
    print("\nLC Tank (1mH, 1µF):")
    print(lc_tank_netlist())
    print("\nExpected resonance:", calculate_lc_resonance(1e-3, 1e-6), "Hz")