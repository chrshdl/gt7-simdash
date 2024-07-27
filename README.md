# gt7-simdash
A toy implementation of a gran turismo 7 dash.

<img width=480px src="https://raw.githubusercontent.com/chrshdl/gt7-simdash/master/gt7-simdash.png" />

Installation
-----
```
$ pipenv run pip install --upgrade wheel
$ pipenv --python 3.10
$ pipenv shell
(gt7-simdash) $ pipenv install
```
Usage
-----
Consider adding the IP address of your PS5 in the `config.json` like
```
"ps5_ip": "192.168.1.30"
```
Start the simdash with `python dash.py`

Whats next
-----
- [x] Improve Feed performance
- [ ] Efficient RPM gauge
- [x] Fix LED bugs
- [x] Calculate current lap time
- [ ] Pause current lap measurement if game paused
- [x] Show simdash in action

