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
or set
```
"ps5_ip": null
```
to run the mockup. Start the simdash with `(gt7-simdash) $ python dash.py`

Whats next
-----
- [x] Improve Feed performance
- [ ] Efficient RPM gauge
- [ ] Fix LED bugs
- [ ] Calculate current lap time
- [ ] Show simdash in action
