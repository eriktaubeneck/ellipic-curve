from dataclasses import dataclass, field
from typing import Union, Tuple
import sys
import secrets
import hashlib
import math
import warnings
import base64

from algebra import ZModField, ZModElement

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash


warning_message = """
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

This code is for DEMO and EDUCATIONAL purposes only. It is NOT SECURE!"""
warnings.warn(
    warning_message +
    "You've imported code that should not be used for cryptograpic purposes."
)


@dataclass(order=True, frozen=True)
class EC:
    """
    a simple EC of the form y^2 = x^3 + a*x + b
    within the field ZModField
    """
    field: ZModField
    a: ZModElement
    b: ZModElement

    @classmethod
    def gen_from_int(cls, field: ZModField, x: int, y: int) -> 'EC':
        return cls(field, field.gen_element(x), field.gen_element(y))

    def gen_element(self, x: Union[int, ZModElement], y: Union[int, ZModElement]) -> 'ECElement':
        if isinstance(x, int):
            x = self.field.gen_element(x)
        if isinstance(y, int):
            y = self.field.gen_element(y)
        return ECElement(x, y, self)

    def generate_elements(self):
        elements = {self.infinity}
        possible_x = self.field.elements
        residues = self.field.quadratic_residues
        for x in possible_x:
            y_sqr = x**3 + self.a * x + self.b
            ys = residues.get(y_sqr, None)
            if ys:
                for y in ys:
                    elements.add(self.gen_element(x, y))
        return elements

    @property
    def infinity(self) -> 'ECElement':
        zero = self.field.gen_element(0)
        return ECElement(zero, zero, self, True)


@dataclass(order=True, frozen=True)
class ECElement:
    x: ZModElement
    y: ZModElement
    ec: 'EC' = field(repr=False)
    infinity: bool = False

    def __post_init__(self):
        if not self.validate() and not self.infinity:
            raise Exception(f'{self} is not a point on {self.ec}')

    def __repr__(self):
        if self.infinity:
            return '(inf)'
        return f'({self.x.value},{self.y.value})'

    def validate(self) -> bool:
        return self.y ** 2 == self.x ** 3 + self.ec.a * self.x + self.ec.b

    def __add__(self, other: 'ECElement') -> 'ECElement':
        p = self
        q = other
        if p == self.ec.infinity:
            return q
        if q == self.ec.infinity:
            return p
        if p.x == q.x and p.y == -q.y:
            return self.ec.infinity
        elif p == q:
            m = ((p.x ** 2) * 3 + self.ec.a) / (p.y * 2)
        else:
            m = (q.y - p.y) / (q.x - p.x)
        x = m**2 - p.x - q.x
        y = m*(p.x - x) - p.y
        return self.ec.gen_element(x, y)

    def __sub__(self, other: 'ECElement') -> 'ECElement':
        return self + -other

    def __mul__(self, other: int) -> 'ECElement':
        bits = f'{other:b}'  # hack to get the bits of other
        value = self
        for bit in bits[1:]:
            prev_value = value
            value = prev_value + prev_value
            if bit == '1':
                value += self
        return value

    def __neg__(self) -> 'ECElement':
        return self.ec.gen_element(self.x, -self.y)

    def generate(self):
        q = self
        elements = {q}
        yield self
        if q == self.ec.infinity:
            return
        new_q = q + q
        while new_q not in elements:
            elements.add(new_q)
            yield new_q
            new_q += q


@dataclass(frozen=True)
class ECC:
    ec: EC
    size: int = field(repr=False)
    generator: ECElement = field(repr=False)
    field: ZModField = field(repr=False, init=False)

    def __post_init__(self):
        warnings.warn(
            warning_message +
            "You've initiated the ECC class that should not be used for cryptograpic purposes."
        )
        object.__setattr__(self, 'field', ZModField(self.size))

    def generate_private_key(self) -> int:
        return secrets.randbelow(self.size)

    def get_public_key(self, private_key: int) -> ECElement:
        return self.generator * private_key

    def generate_key_pair(self) -> Tuple[int, ECElement]:
        private_key = self.generate_private_key()
        return (private_key, self.get_public_key(private_key))

    def hash(self, message: bytes) -> ZModElement:
        h = int.from_bytes(
            hashlib.blake2b(message, digest_size=math.ceil(math.log(self.size, 2)/8)).digest(),
            sys.byteorder
        )
        return self.field.gen_element(h)

    def sign(self, message: bytes, private_key: int) -> Tuple[ZModElement, ZModElement]:
        warnings.warn(
            warning_message +
            "You've signed a message with code that should not be used for cryptograpic purposes."
        )
        h: ZModElement = self.hash(message)
        k, kG = self.generate_key_pair()
        r: ZModElement = self.field.gen_element(kG.x.value)
        s: ZModElement = (h + r * private_key) / k
        return (r, s)

    def verify(
            self,
            message: bytes,
            signature: Tuple[ZModElement, ZModElement],
            public_key: ECElement
    ) -> bool:
        warnings.warn(
            warning_message +
            "You've verified a signature with code that should not be used "
            "for cryptograpic purposes."
        )
        r: ZModElement
        s: ZModElement
        r, s = signature
        h: ZModElement = self.hash(message)
        w: ZModElement = ~s
        u: ZModElement = w * h
        v: ZModElement = w * r
        Q: ECElement = (self.generator*u.value) + (public_key*v.value)
        return self.field.gen_element(Q.x.value) == r

    def symetric_key_derivation_scheme(
            self,
            shared_secret: ECElement,
            iterations: int = 100000
    ) -> bytes:
        kdf = ConcatKDFHash(
            algorithm=hashes.SHA256(),
            length=32,
            otherinfo=b'elliptic-curve-demo',
        )
        shared_secret_bytes: bytes = shared_secret.x.value.to_bytes(
            (shared_secret.x.value.bit_length() + 7) // 8,
            byteorder=sys.byteorder
        )
        key = base64.urlsafe_b64encode(kdf.derive(shared_secret_bytes))
        return key

    def encrypt(self, message: bytes, public_key: ECElement) -> Tuple[bytes, ECElement]:
        warnings.warn(
            warning_message +
            "You've encrypted a message with code that should not be used "
            "for cryptograpic purposes."
        )
        d: int = self.generate_private_key()
        ephemeral_key: ECElement = self.generator * d
        shared_secret: ECElement = public_key * d
        key = self.symetric_key_derivation_scheme(shared_secret)
        f = Fernet(key)
        token = f.encrypt(message)
        return (token, ephemeral_key)

    def decrypt(self, message: bytes, ephemeral_key: ECElement, private_key: int) -> bytes:
        warnings.warn(
            warning_message +
            "You've decrypted a token with code that should not be used "
            "for cryptograpic purposes."
        )
        shared_secret: ECElement = ephemeral_key * private_key
        key = self.symetric_key_derivation_scheme(shared_secret, iterations=1)
        f = Fernet(key)
        return f.decrypt(message)
