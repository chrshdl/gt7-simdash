# Gran Turismo 7 digital display

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<div align="center">

[![GT7 SIMDASH IN ACTION](https://img.youtube.com/vi/Pckp1NWW3_M/0.jpg)](https://www.youtube.com/watch?v=Pckp1NWW3_M)

<h3>

 [Video 1](https://www.youtube.com/watch?v=Pckp1NWW3_M) | [Documentation](https://github.com/chrshdl/gt7-simdash/wiki)

</h3>

</div>

---

This is a very simple, lightweight HMI for a Gran Turismo 7 digital display. Written in Python and based on an event-driven architecture, it aims to be the easiest framework to add new features to.

## Installation

The codebase uses `uv` for managing the dependencies and the virtual environment. Follow the [installation guide for uv](https://docs.astral.sh/uv/#installation). From the repo root execute

```
uv venv
source .venv/bin/activate
uv sync
```

## Usage

Start the application from inside the virtual environment with `python main.py`. Enter the IP of your Playstation using the buttons and press OK. The application will attempt to establish a connection with the Playstation. 

<div align="left">
<picture>
  <img width=600px src="https://raw.githubusercontent.com/chrshdl/gt7-simdash/main/assets/gt7-simdash-enter-ip.png" />
</picture>

If the Playstation isn't ready to connect yet (because powered off) you will see a waiting screen. Power on your Playstation and start Gran Turismo 7. Once the opening trailer is shown the application will automatically connect and change to the initial view. Now you are ready to go. Start a race to trigger a car update and the dashboard will show the corresponding telemetry data.

<picture>
  <img width=600px src="https://raw.githubusercontent.com/chrshdl/gt7-simdash/main/assets/gt7-simdash-connecting.png" />
</picture>
</div>



## Whats next

- [x] ~~Improve Feed performance~~
- [x] ~~Efficient RPM gauge~~
- [x] ~~Fix LED bugs~~
- [x] ~~Calculate current lap time~~
- [x] ~~Pause current lap measurement if game paused~~
- [x] ~~Show simdash in action~~
- [x] ~~Draw "init" screen on boot / errors~~
- [x] ~~Implement "Set up a new device"~~
- [x] ~~Minimap refinement~~
- [ ] Documentation + quick start guide

## License
All of my code is MIT licensed. Libraries follow their respective licenses.
