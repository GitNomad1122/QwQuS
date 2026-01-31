"""
Custom tool for Qwen-Agent — QUCS-S integration
"""
from qwen_agent.tools import BaseTool
from qwqus.core.simulator import CircuitSimulator
from qwqus.core.netlist import rc_lowpass_netlist, rc_highpass_netlist, opamp_inverting_amplifier, calculate_rc_cutoff
import json
from typing import Dict, Any


class QucsSimulator(BaseTool):
    """
    Tool for running simulations in QUCS-S via Qwen-Agent
    
    Example usage by agent:
    {
      "name": "qucs_simulator",
      "arguments": {
        "circuit_type": "rc_lowpass",
        "r_ohm": 1000,
        "c_farad": 1e-7,
        "analysis_type": "ac",
        "f_start": 1,
        "f_stop": 1000000
      }
    }
    """
    
    def __init__(self):
        super().__init__()
        self.name = 'qucs_simulator'
        self.description = (
            "Simulates electronic circuits using QUCS-S. "
            "Supports RC filters, op-amp circuits. "
            "Returns frequency response data for visualization."
        )
        self.parameters = {
            'type': 'object',
            'properties': {
                'circuit_type': {
                    'type': 'string',
                    'description': 'Type of circuit: "rc_lowpass", "rc_highpass", "opamp_inverting"',
                    'enum': ['rc_lowpass', 'rc_highpass', 'opamp_inverting']
                },
                'r_ohm': {
                    'type': 'number',
                    'description': 'Resistor value in Ohms (for RC circuits)'
                },
                'c_farad': {
                    'type': 'number',
                    'description': 'Capacitor value in Farads (for RC circuits)'
                },
                'analysis_type': {
                    'type': 'string',
                    'description': 'Analysis type: "ac", "dc", "transient"'
                },
                'f_start': {
                    'type': 'number',
                    'description': 'Start frequency in Hz (for AC analysis)'
                },
                'f_stop': {
                    'type': 'number',
                    'description': 'Stop frequency in Hz (for AC analysis)'
                }
            },
            'required': ['circuit_type', 'analysis_type']
        }
        # Use mock mode by default for safety
        self.simulator = CircuitSimulator(use_mock=True)
    
    def _run(self, params: Dict[str, Any]) -> str:
        try:
            # Parse parameters
            p = params
            
            # Select circuit generator
            circuit_type = p.get("circuit_type", "rc_lowpass")
            r = p.get("r_ohm", 1000)
            c = p.get("c_farad", 100e-9)
            
            if circuit_type == "rc_lowpass":
                netlist = rc_lowpass_netlist(r_ohm=r, c_farad=c)
            elif circuit_type == "rc_highpass":
                netlist = rc_highpass_netlist(r_ohm=r, c_farad=c)
            elif circuit_type == "opamp_inverting":
                r1 = p.get("r1_ohm", 1000)
                r2 = p.get("r2_ohm", 10000)
                netlist = opamp_inverting_amplifier(r1_ohm=r1, r2_ohm=r2)
            else:
                return f'Error: unknown circuit type "{circuit_type}"'
            
            # Run simulation
            analysis = p.get("analysis_type", "ac")
            f_start = p.get("f_start", 1)
            f_stop = p.get("f_stop", 1e6)
            
            result = self.simulator.simulate(
                netlist,
                analysis_type=analysis,
                f_start=f_start,
                f_stop=f_stop
            )
            
            # Form human-readable response
            fc_estimated = calculate_rc_cutoff(r, c) if circuit_type in ["rc_lowpass", "rc_highpass"] else None
            
            response = {
                "status": "success",
                "circuit_type": circuit_type,
                "analysis_type": analysis,
                "data": result.to_dict(),
                "summary": f"Simulated {circuit_type} circuit"
            }
            
            if fc_estimated:
                response["summary"] += f" (estimated fc = {fc_estimated:.1f} Hz)"
            
            return json.dumps(response, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e),
                "note": "Mock simulation used (QUCS-S not installed or netlist parsing not implemented yet)"
            }, ensure_ascii=False, indent=2)


# For backward compatibility
__all__ = ["QucsSimulator"]