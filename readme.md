# Exploring Elliptic Curves with Python
```
▓█████▄  ▄▄▄       ███▄    █   ▄████ ▓█████  ██▀███
▒██▀ ██▌▒████▄     ██ ▀█   █  ██▒ ▀█▒▓█   ▀ ▓██ ▒ ██▒
░██   █▌▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░▒███   ▓██ ░▄█ ▒
░▓█▄   ▌░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓▒▓█  ▄ ▒██▀▀█▄
░▒████▓  ▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒░▒████▒░██▓ ▒██▒
 ▒▒▓  ▒  ▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
 ░ ▒  ▒   ▒   ▒▒ ░░ ░░   ░ ▒░  ░   ░  ░ ░  ░  ░▒ ░ ▒░
 ░ ░  ░   ░   ▒      ░   ░ ░ ░ ░   ░    ░     ░░   ░
   ░          ░  ░         ░       ░    ░  ░   ░
 ░
```
This code is for DEMO and EDUCATIONAL purposes only. It is NOT SECURE!

If you are looking for a package for actual cryptographic usage, check out [pyca/cryptography](https://cryptography.io/en/latest/).


## Usage

If you want to play with this code, clone this repo and create a virtual environment.

Install requirements with

```
pip install -r requirements.txt
```

The code as written should pass type checks with

```
mypy .
```

Additionally, there are tests that can be run with

```
nose2
```

## Warning Message

The warning message (also at the top of this readme) will appear if you import this code, and if you call any of the dangerous methods. THIS CODE IS JUST FOR LEARNING, and should not be used for actual cryptographic usage.

If you run the test, you'll see this warning message a handful of times. This is on purpose.

## References

I wrote this code working primarily from chapter 12 of [Serious Cryptography](https://nostarch.com/seriouscrypto), which is an awesome resource if you are looking to learn more about cryptography.

The [Elliptic Curve Digital Signature Algorithm](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm) Wikipedia page was also helpful.

The specific Elliptic Curve used in the `ECCTest`, secp256k1, came from [safecurves.cr.yp.to](https://safecurves.cr.yp.to/). It should be noted that this curve is listed as NOT SAFE. (However it fits the form that I implemented and is used in Serious Cryptography.) Again, this is for LEARNING purposes only.
