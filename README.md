# Gran Turismo 7 digital display
<div align="center">

<picture>
<img width=480px src="https://raw.githubusercontent.com/chrshdl/gt7-simdash/main/assets/thumbnail.png" />
</picture>

<h3>

| [Video](https://youtu.be/qh3pYMYFU8I) | [Documentation](https://github.com/chrshdl/gt7-simdash/wiki) |

</h3>

</div>

---

This is a very simple, lightweight HMI for a Gran Turismo 7 digital display. Written in Python and based on an event-driven architecture, it aims to be the easiest framework to add new features to.

## Install on Raspberry Pi with Blinkt! LED

First do a `pip3 install pipenv` to install the virtualenv management tool. After that edit `~/.profile` and check if `PATH` includes the user's private bin.

```sh
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
```

Source it by executing `source ~/.profile`. Now you are ready do create the virtual environment and install all dependencies needed by the project. From the repo root execute:

```sh
pipenv --python 3
pipenv shell
pipenv install
```

## Usage

Consider adding the IP address of your Playstation 5 in the `config.json` like

```json
"playstation_ip": "192.168.1.30"
```
Start the application from inside the virtual environment with `python main.py`

## Whats next

- [x] ~~Improve Feed performance~~
- [x] ~~Efficient RPM gauge~~
- [x] ~~Fix LED bugs~~
- [x] ~~Calculate current lap time~~
- [x] ~~Pause current lap measurement if game paused~~
- [x] ~~Show simdash in action~~
- [x] ~~Draw "init" screen on boot / errors~~
- [ ] Implement "Set up a new device"
- [ ] Documentation + quick start guide

## License
All of my code is MIT licensed. Libraries follow their respective licenses.
