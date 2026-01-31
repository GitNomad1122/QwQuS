"""
Netlist templates for common circuits
"""


class NetlistTemplates:
    """
    Collection of netlist templates for common electronic circuits
    """
    
    @staticmethod
    def rc_low_pass(R_value: str = "1k", C_value: str = "1uF", Vin: str = "1") -> str:
        """
        Generate netlist for RC low-pass filter
        """
        return f"""* RC Low Pass Filter
V1 in 0 DC 0 AC {Vin}
R1 in out {R_value}
C1 out 0 {C_value}
.control
ac dec 10 1 1MEG
.print ac v(out)
.end
.end
"""

    @staticmethod
    def rc_high_pass(R_value: str = "1k", C_value: str = "1uF", Vin: str = "1") -> str:
        """
        Generate netlist for RC high-pass filter
        """
        return f"""* RC High Pass Filter
V1 in 0 DC 0 AC {Vin}
C1 in out {C_value}
R1 out 0 {R_value}
.control
ac dec 10 1 1MEG
.print ac v(out)
.end
.end
"""

    @staticmethod
    def voltage_divider(R1_value: str = "1k", R2_value: str = "1k", Vin: str = "1") -> str:
        """
        Generate netlist for voltage divider
        """
        return f"""* Voltage Divider
V1 in 0 DC {Vin} AC 1
R1 in mid {R1_value}
R2 mid 0 {R2_value}
.control
dc V1 0 5 0.1
.print dc v(mid)
.end
.end
"""

    @staticmethod
    def common_em_amplifier(beta: str = "100", Rc: str = "2k", Re: str = "1k", R1: str = "10k", R2: str = "10k", 
                           Vcc: str = "12", Vin: str = "0.1") -> str:
        """
        Generate netlist for common emitter amplifier
        """
        return f"""* Common Emitter Amplifier
Vcc collector 0 DC {Vcc}
V1 base 0 DC 0 AC {Vin}
R1 base collector {R1}
R2 emitter 0 {R2}
Rc collector collector_int {Rc}
Re emitter 0 {Re}
Q1 collector_int base emitter qmodel
.model qmodel npn bf={beta}
.control
ac dec 10 1 1MEG
.print ac v(collector)
.end
.end
"""

    @staticmethod
    def opamp_buffer(Vin: str = "1") -> str:
        """
        Generate netlist for opamp buffer (ideal model)
        """
        return f"""* Opamp Buffer
Vin in 0 AC {Vin}
E1 out 0 in 0 1e6  ; Ideal opamp with high gain
.control
ac dec 10 1 1MEG
.print ac v(out)
.end
.end
"""

    @staticmethod
    def lc_tank(L_value: str = "1mH", C_value: str = "1uF") -> str:
        """
        Generate netlist for LC tank circuit
        """
        return f"""* LC Tank Circuit
I1 0 node1 DC 0 AC 1mA
R1 node1 0 1Meg  ; Current source resistance
L1 node1 node2 {L_value}
C1 node2 0 {C_value}
.control
ac dec 10 1k 100MEG
.print ac v(node2)
.end
.end
"""

    @staticmethod
    def diode_rectifier(D_model: str = "default", R_load: str = "1k", Vin: str = "10", freq: str = "60") -> str:
        """
        Generate netlist for diode rectifier
        """
        return f"""* Diode Rectifier
V1 in 0 SIN(0 {Vin} {freq})
D1 out in {D_model}
R1 out 0 {R_load}
.model {D_model} d
.control
tran 1m 100m
.print tran v(out)
.end
.end
"""