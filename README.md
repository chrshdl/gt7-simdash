# gt7-simdash
A toy implementation of a granturismo 7 dash.

<img width=820px src="https://raw.githubusercontent.com/chrshdl/gt7-simdash/master/example.png" />

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
to run the mockup. After that start the simdash with `(gt7-simdash) $ ./main.py`
