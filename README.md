# QwQuS — AI-Powered Circuit Simulation with Qwen-Agent + QUCS-S

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**QwQuS** (pronounced *«kwiks»*) bridges **Qwen-Agent** (Alibaba's AI agent platform) and **QUCS-S** (electronic circuit simulator), enabling circuit design and analysis through natural language.

> "Design an active low-pass filter at 1 kHz with an op-amp" → Agent generates the circuit, runs simulation, and shows frequency response.

## ✨ Features

- Generate netlists from natural language descriptions
- Automatically run simulations (AC/DC/Transient)
- Visualize results through matplotlib
- Support for common circuits: filters, amplifiers, oscillators
- Cross-platform support (Windows/Linux/macOS)

## 🚀 Quick Start

```bash
# 1. Install QUCS-S: https://github.com/ra3xdh/qucs_s/releases
# 2. Set up environment
git clone https://github.com/GitNomad1122/QwQuS.git
cd QwQuS
python -m venv venv && venv\Scripts\activate  # On Windows
# venv/bin/activate  # On Linux/Mac
pip install -e .

# 3. Run an example
python examples/rc_lowpass_demo.py
```

## 📁 Project Structure

```
QwQuS/
├── README.md                 # Project overview
├── LICENSE                   # MIT License
├── requirements.txt          # Dependencies
├── setup.py                  # Package installation
├── qwqus/                    # Main package
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── qucs_simulator.py # Custom QUCS simulator tool
│   └── utils/
│       ├── __init__.py
│       ├── netlist_templates.py # Circuit templates
│       └── dat_parser.py        # QUCS output parser
└── examples/
    ├── rc_lowpass_demo.py       # RC filter example
    ├── transistor_amp_demo.py   # Amplifier example
    └── agent_webui.py           # Web interface for agent
```

## 🛠️ Usage Examples

### Run a Simple Simulation

```python
from qwqus.tools.qucs_simulator import QucsSimulator
from qwqus.utils.netlist_templates import NetlistTemplates

simulator = QucsSimulator()

# Create an RC low-pass filter
rc_netlist = NetlistTemplates.rc_low_pass(R_value="1k", C_value="1uF")

# Run simulation
result = simulator._run(
    netlist=rc_netlist,
    analysis_type='ac',
    output_vars=['frequency', 'out']
)
```

### Natural Language Circuit Design

```python
from examples.agent_webui import create_circuit_design_agent

agent = create_circuit_design_agent()
# Now you can interact with the agent using natural language
```

## 🤝 Contributing

We welcome contributions! Please see our [Issues](https://github.com/GitNomad1122/QwQuS/issues) page for ways to contribute.

## 📄 License

MIT — freely use in personal and commercial projects.