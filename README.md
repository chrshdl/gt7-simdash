## Gran Turismo 7 Instrument Cluster

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This is an HMI for a Gran Turismo 7 Instrument Cluster. It is written in Python and based on a revised state/event architecture.

![GT7-Simdash](screenshots/05_gt7-simdash-dashboard.png)

## Installation

The codebase uses `uv` for managing the dependencies and the virtual environment. Follow the [installation guide for uv](https://docs.astral.sh/uv/#installation). From the repo root execute

```
uv venv
source .venv/bin/activate
uv sync
```

If your environment is pointing to an old [granturismo](https://github.com/chrshdl/granturismo) lib dependency consider running `uv lock --upgrade` and `uv sync`.

## Raspberry Pi

This is a quick and easy way to install GT7-Simdash to a microSD card, ready to use with your Raspberry Pi. To manually download the latest version, see the list below.

[![Download Pi 4 Image](https://img.shields.io/badge/download-pi4--image-blue?logo=raspberry-pi)](https://github.com/chrshdl/gt7-simdash/releases/download/latest/sdcard-raspberrypi4.img)



## License
All of my code is MIT licensed. Libraries follow their respective licenses.