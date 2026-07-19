# This code will set up smartpark as a module.
# This step is not necessary for data science students.
from setuptools import find_packages, setup

setup(
    name="smartpark",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "paho-mqtt",
        "sense-hat",
        "tkinter",
        "toml"
    ],
    entry_points={
        "console_scripts": [
            "smartpark = smartpark.main:main",
        ],
    },
    python_requires=">=3.10",
)
