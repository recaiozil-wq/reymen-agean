from setuptools import setup

setup(
    name="reymen-agent",
    version="0.1.0",
    description="ReYMeN AI Agent",
    py_modules=["reymen_launcher"],
    entry_points={
        "console_scripts": [
            "reymen = reymen_launcher:main",
        ],
    },
)
