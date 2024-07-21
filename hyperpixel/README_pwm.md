## Setup

    sudo apt install build-essential pigpio
    gcc -Wall -pthread -o pwm pwm.c -lpigpio -lrt
    sudo ./pwm 19 1000000 160000

## pwm arguments

    (1) GpioNumber, (2) Freq, (3) DutyCycle
    Freq: 0 (off) or 1-125000000 (125M)
    DutyCycle: 0 (off) to 1000000 (1M)(fully on)

## examples
    very dim: sudo ./pwm 19 1000000 135000
    max brightness: sudo ./pwm 19 1000000 1000000

## Sources

- https://www.codecubix.eu/linux/hardware-pwm-with-raspberry-pi-zero/
- http://abyz.me.uk/rpi/pigpio/cif.html#gpioHardwarePWM
- https://pinout.xyz/pinout/hyperpixel4

