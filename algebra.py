from dataclasses import dataclass, field
from typing import Union, Dict, Iterator, List
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
