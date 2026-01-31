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
- **NEW**: Works with mock simulator when QUCS-S is not installed for development/testing

## 🚀 Quick Start

```bash
# 1. Install QUCS-S (optional, for real simulations): https://github.com/ra3xdh/qucs_s/releases
#    Without QUCS-S, the system uses mock simulations for development/testing
# 2. Set up environment
git clone https://github.com/GitNomad1122/QwQuS.git
cd QwQuS
python -m venv venv && venv\Scripts\activate  # On Windows
# venv/bin/activate  # On Linux/Mac
pip install -e .

# 3. Run an example
python examples/rc_filter_demo.py
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
│   ├── core/                 # Core simulation functionality
│   │   ├── __init__.py
│   │   ├── simulator.py      # QUCS integration (with mock fallback)
│   │   └── netlist.py        # Netlist generation
│   ├── tools/                # Qwen-Agent integration tools
│   │   ├── __init__.py
│   │   └── qucs_simulator.py # Custom Qwen-Agent tool
│   └── utils/
│       ├── __init__.py
│       ├── netlist_templates.py # Circuit templates
│       └── dat_parser.py        # QUCS output parser
└── examples/
    ├── rc_filter_demo.py        # RC filter example (with visualization)
    ├── rc_lowpass_demo.py       # RC filter example (alternative)
    ├── transistor_amp_demo.py   # Amplifier example
    └── agent_webui.py           # Web interface for agent
```

## 🛠️ Installation & Usage

### Basic Installation
```bash
pip install -e .
```

### With Full Qwen-Agent Integration
```bash
pip install -e ".[agent]"
# or
pip install -e . "qwen-agent[gui,code_interpreter]>=1.1.0"
```

### Running Examples
```bash
# Basic RC filter simulation (works with or without QUCS-S)
python examples/rc_filter_demo.py

# With Qwen-Agent integration (requires full installation)
python examples/agent_webui.py
```

## 🧪 Testing Without QUCS-S

The system includes a mock simulator that generates realistic data for common circuits when QUCS-S is not installed. This allows development and testing without requiring the full QUCS-S installation.

## 🤝 Contributing

We welcome contributions! Please see our [Issues](https://github.com/GitNomad1122/QwQuS/issues) page for ways to contribute.

### Development Setup
```bash
# Clone and install in development mode
git clone https://github.com/GitNomad1122/QwQuS.git
cd QwQuS
pip install -e .
```

## 📄 License

MIT — freely use in personal and commercial projects.