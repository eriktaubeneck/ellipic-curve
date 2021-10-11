from dataclasses import dataclass, field
from typing import Union, Dict, Tuple, Iterator, List
import sys
import secrets
import hashlib
import math
import warnings


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
warnings.warn(warning_message)


@dataclass(frozen=True)
class ZModField:
    size: int

    def gen_element(self, value: int, strict: bool = False) -> 'ZModElement':
        if not strict:
            value = value % self.size
        return ZModElement(value, self)

    @property
    def elements(self) -> Iterator['ZModElement']:
        for i in range(self.size):
            yield self.gen_element(i, strict=True)

    @property
    def quadratic_residues(self) -> Dict['ZModElement', List['ZModElement']]:
        residues: Dict['ZModElement', List['ZModElement']] = {}
        for e in self.elements:
            e_sqr = pow(e, 2)
            v = residues.get(e_sqr, [])
            v.append(e)
            residues[e_sqr] = v
        return residues


@dataclass(order=True, frozen=True)
class ZModElement:
    value: int = field(compare=True)
    field: ZModField

    def __post_init__(self):
        if not 0 <= self.value < self.field.size:
            raise Exception(
                f'{self.value} is an invalid element of {self.field}'
            )

    def __add__(self, other: Union[int, 'ZModElement']) -> 'ZModElement':
        if isinstance(other, int):
            other = self.field.gen_element(other, strict=True)
        if self.field != other.field:
            raise Exception(
                f'cannot add two elements of different '
                f'fields: {self.field} and {other.field}'
            )
        value = (self.value + other.value) % self.field.size
        return self.__class__(value, self.field)

    def __sub__(self, other: Union[int, 'ZModElement']) -> 'ZModElement':
        if isinstance(other, int):
            other = self.field.gen_element(other, strict=True)
        if self.field != other.field:
            raise Exception(
                f'cannot subtract two elements of different '
                f'fields: {self.field} and {other.field}'
            )
        value = (self.value - other.value) % self.field.size
        return self.__class__(value, self.field)

    def __mul__(self, other: Union[int, 'ZModElement']) -> 'ZModElement':
        if isinstance(other, int):
            other = self.field.gen_element(other, strict=True)
        value = (self.value * other.value) % self.field.size
        return self.__class__(value, self.field)

    def __truediv__(self, other: Union[int, 'ZModElement']) -> 'ZModElement':
        if isinstance(other, int):
            other = self.field.gen_element(other, strict=True)
        return self * ~other

    def __floordiv__(self, other: Union[int, 'ZModElement']) -> 'ZModElement':
        if isinstance(other, int):
            other = self.field.gen_element(other, strict=True)
        value = (self.value // other.value) % self.field.size
        return self.__class__(value, self.field)

    def __pow__(self, other: int, modulo=None) -> 'ZModElement':
        if modulo is not None:
            raise Exception('Cannot specify modulo for a ZModElement')
        value = pow(self.value, other, self.field.size)
        return self.__class__(value, self.field)

    def __repr__(self) -> str:
        return f'{self.value}mod{self.field.size}'

    def __neg__(self) -> 'ZModElement':
        return self.field.gen_element(-self.value, strict=False)

    def __pos__(self) -> 'ZModElement':
        return self

    def __invert__(self) -> 'ZModElement':
        """ Extended Euclidean algorithm"""
        if self.value == 0:
            raise Exception('{self} cannot be inverted')
        zero: 'ZModElement' = self.field.gen_element(0)
        one: 'ZModElement' = self.field.gen_element(1)
        q: 'ZModElement' = self.field.gen_element(self.field.size // self.value)
        t: 'ZModElement' = one
        new_t: 'ZModElement' = zero - q
        r: 'ZModElement' = self
        new_r: 'ZModElement' = zero - q * self

        while new_r != zero:
            q = r // new_r
            t, new_t = new_t, t - q * new_t
            r, new_r = new_r, r - q * new_r

        if r > one:
            raise Exception(f'{self} has no inverse')
        return t


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
        r: ZModElement
        s: ZModElement
        r, s = signature
        h: ZModElement = self.hash(message)
        w: ZModElement = ~s
        u: ZModElement = w * h
        v: ZModElement = w * r
        Q: ECElement = (self.generator*u.value) + (public_key*v.value)
        return self.field.gen_element(Q.x.value) == r

    def encrypt(self, message: bytes, public_key: ECElement) -> bytes:
        ...

    def decrypt(self, message: bytes, private_key: int) -> bytes:
        ...
