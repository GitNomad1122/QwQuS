from setuptools import setup, find_packages

setup(
    name="qwqus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "qwen-agent[gui,code_interpreter]>=1.1.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "json5>=0.9.0",
    ],
    python_requires=">=3.10",
    author="GitNomad1122",
    description="AI-powered circuit simulation with Qwen-Agent and QUCS-S",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GitNomad1122/QwQuS",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
)