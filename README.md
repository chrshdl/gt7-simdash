# Gran Turismo 7 digital display
<div align="center">

<picture>
<img width=480px src="https://raw.githubusercontent.com/chrshdl/gt7-simdash/master/gt7-simdash.png" />
</picture>

</div>

---

This is a very simple, lightweight HMI for a Gran Turismo 7 digital display. Written in Python and based on an event-driven architecture, it aims to be the easiest framework to add new features to.

## Installation

```sh
pipenv run pip install --upgrade wheel
pipenv --python 3.10
pipenv shell
pipenv install
```
## Usage

Consider adding the IP address of your Playstation 5 in the `config.json` like

```json
"ps5_ip": "192.168.1.30"
```
Start with `python dash.py`

## Whats next

- [x] Improve Feed performance
- [ ] Efficient RPM gauge
- [x] Fix LED bugs
- [x] Calculate current lap time
- [ ] Pause current lap measurement if game paused
- [x] Show simdash in action

## License
All of my code is MIT licensed. Libraries follow their respective licenses.
