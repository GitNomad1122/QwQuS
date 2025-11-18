setup(
    name="qwqus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "qwen-agent[gui,code_interpreter]",
        "numpy",
        "pandas",
        "matplotlib",
    ],
    python_requires=">=3.10",
    author="Your Name",
    description="Qwen-Agent + QUCS integration for AI-driven circuit simulation",
    license="MIT",
)
