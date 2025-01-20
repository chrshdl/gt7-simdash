from setuptools import find_packages, setup

setup(
    name="gt7simdash",
    version="0.0.1",
    description="A toy implementation of a Gran Turismo 7 digital display.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pygame",
        "blinkt",
        "rpi-lgpio",
        "scipy",
        "granturismo @ git+https://github.com/chrshdl/granturismo@main",
    ],
)