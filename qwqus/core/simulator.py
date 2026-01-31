"""
QUCS Circuit Simulator — real and mock modes
"""
import os
import subprocess
import tempfile
import json
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class SimulationResult:
    """Simulation result with convenient interface for visualization"""
    frequencies: np.ndarray  # Hz
    magnitude: np.ndarray    # Volts or relative units
    phase: Optional[np.ndarray] = None  # degrees
    
    @property
    def magnitude_db(self) -> np.ndarray:
        return 20 * np.log10(np.maximum(self.magnitude, 1e-12))
    
    def to_dict(self) -> Dict[str, list]:
        return {
            "frequencies_hz": self.frequencies.tolist(),
            "magnitude": self.magnitude.tolist(),
            "magnitude_db": self.magnitude_db.tolist(),
            "phase_deg": self.phase.tolist() if self.phase is not None else None
        }


class CircuitSimulator:
    """
    QUCS-S simulator wrapper with automatic fallback to mock mode
    """
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.qucsator_path = self._find_qucsator() if not use_mock else None
        
        if not use_mock and not self.qucsator_path:
            print("⚠️  Qucsator not found — switching to mock mode")
            self.use_mock = True
    
    def _find_qucsator(self) -> Optional[str]:
        """Auto-detection of qucsator path on different OS"""
        candidates = [
            # Windows
            r"C:\Program Files\Qucs-S\bin\qucsator.exe",
            r"C:\Program Files (x86)\Qucs-S\bin\qucsator.exe",
            r"C:\Program Files\Qucs-S\bin\qucsator_rf.exe",  # Alternative name
            # Linux
            "/usr/bin/qucsator",
            "/usr/local/bin/qucsator",
            # macOS (Homebrew)
            "/opt/homebrew/bin/qucsator",
            "/usr/local/bin/qucsator",
        ]
        
        # Check PATH environment variable
        for path in os.environ.get("PATH", "").split(os.pathsep):
            candidate = os.path.join(path, "qucsator.exe" if os.name == "nt" else "qucsator")
            if os.path.exists(candidate):
                return candidate
        
        # Check alternative executable name
        for path in os.environ.get("PATH", "").split(os.pathsep):
            candidate = os.path.join(path, "qucsator_rf.exe" if os.name == "nt" else "qucsator_rf")
            if os.path.exists(candidate):
                return candidate
        
        # Check hardcoded paths
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        
        return None
    
    def simulate(self, netlist: str, analysis_type: str = "ac", **params) -> SimulationResult:
        """
        Run simulation
        
        Args:
            netlist: QUCS netlist text
            analysis_type: "ac", "dc", "transient"
            **params: Analysis parameters (f_start, f_stop, etc.)
        
        Returns:
            SimulationResult with data for visualization
        """
        if self.use_mock:
            return self._mock_simulation(analysis_type, **params)
        else:
            return self._real_simulation(netlist, analysis_type, **params)
    
    def _real_simulation(self, netlist: str, analysis_type: str, **params) -> SimulationResult:
        """Real simulation via qucsator"""
        if not self.qucsator_path:
            raise RuntimeError("qucsator not found and mock mode disabled")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            net_path = Path(tmpdir) / "circuit.net"
            dat_path = Path(tmpdir) / "results.dat"
            
            # Save netlist
            net_path.write_text(netlist, encoding="utf-8")
            
            # Form command
            cmd = [
                self.qucsator_path,
                "-i", str(net_path),
                "-o", str(dat_path)
            ]
            
            try:
                # Run simulation
                result = subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=30  # 30 seconds max
                )
                
                if result.returncode != 0:
                    # Try to extract useful error from stderr
                    error_msg = result.stderr or result.stdout
                    raise RuntimeError(f"Simulation error:\n{error_msg[:500]}")
                
                # Parse results (simplified parser for MVP)
                if not dat_path.exists():
                    raise FileNotFoundError(f"Results not found: {dat_path}")
                
                return self._parse_qucs_dat(dat_path, analysis_type)
                
            except subprocess.TimeoutExpired:
                raise TimeoutError("Simulation exceeded time limit (30 sec)")
            except Exception as e:
                # On error — fallback to mock for demonstration
                print(f"⚠️  Real simulation error: {e}")
                print("    Switching to mock mode for demonstration...")
                return self._mock_simulation(analysis_type, **params)
    
    def _parse_qucs_dat(self, dat_path: Path, analysis_type: str) -> SimulationResult:
        """
        Simplified .dat file parser for QUCS (MVP)
        Full parser would be needed in production
        """
        # For MVP returning mock data with note
        print(f"ℹ️  .dat file parsing will be implemented in next version")
        return self._mock_simulation(analysis_type, note="mocked_due_to_parser_limitation")
    
    def _mock_simulation(self, analysis_type: str, **params) -> SimulationResult:
        """Mock simulation for demonstration without installed QUCS-S"""
        f_start = params.get("f_start", 1)
        f_stop = params.get("f_stop", 1e6)
        
        # Generate logarithmic frequency scale
        frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), 200)
        
        if analysis_type == "ac":
            # RC low-pass filter response (fc = 1.59 kHz for R=1k, C=100nF)
            fc = 1 / (2 * np.pi * 1000 * 100e-9)
            magnitude = 1 / np.sqrt(1 + (frequencies / fc) ** 2)
            phase = -np.arctan(frequencies / fc) * 180 / np.pi
            return SimulationResult(frequencies, magnitude, phase)
        
        elif analysis_type == "dc":
            # Just constant voltage
            return SimulationResult(
                np.array([0.0]),
                np.array([params.get("voltage", 5.0)])
            )
        
        else:  # transient
            t = np.linspace(0, 1e-3, 500)
            signal = np.sin(2 * np.pi * 1000 * t) * np.exp(-t / 0.2e-3)
            return SimulationResult(t, signal)


# Export for convenience
__all__ = ["CircuitSimulator", "SimulationResult"]