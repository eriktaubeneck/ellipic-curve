import unittest
import logging

from algebra import ZModField
from elliptic_curve import EC, ECC


class BaseTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.field = ZModField(191)


class ZModElementTest(BaseTest):

    def test_addtion(self):
        x = self.field.gen_element(5)
        y = self.field.gen_element(4)

        z = self.field.gen_element(9)
        self.assertEqual(x+y, z)

        x = self.field.gen_element(180)
        y = self.field.gen_element(30)

        z = self.field.gen_element(19)
        self.assertEqual(x+y, z)

    def test_multiplication(self):
        x = self.field.gen_element(5)
        y = self.field.gen_element(4)

        z = self.field.gen_element(20)
        self.assertEqual(x*y, z)

        x = self.field.gen_element(20)
        y = self.field.gen_element(10)

        z = self.field.gen_element(9)
        self.assertEqual(x*y, z)

    def test_pow(self):
        x = self.field.gen_element(5)
        z = self.field.gen_element(25)
        self.assertEqual(x**2, z)

    def test_equality(self):
        one = self.field.gen_element(1)
        _one = self.field.gen_element(1)
        self.assertEqual(one, _one)
        x = self.field.gen_element(5)
        y = self.field.gen_element(4)
        self.assertNotEqual(x, y)

    def test_inverse(self):
        x = self.field.gen_element(8)
        y = ~x
        z = self.field.gen_element(1)
        self.assertEqual(x*y, z)
        self.assertEqual(y*x, z)
        self.assertEqual(x/z, x)

    def test_elements(self):
        self.field = ZModField(7)
        self.assertSequenceEqual(
            [
                self.field.gen_element(0),
                self.field.gen_element(1),
                self.field.gen_element(2),
                self.field.gen_element(3),
                self.field.gen_element(4),
                self.field.gen_element(5),
                self.field.gen_element(6),
             ],
            list(self.field.elements)
        )

    def test_quadratic_residues(self):
        self.field = ZModField(7)
        e = self.field.gen_element
        self.assertDictEqual(
            {
                e(0): [e(0), ],
                e(1): [e(1), e(6), ],
                e(2): [e(3), e(4), ],
                e(4): [e(2), e(5), ],
            },
            self.field.quadratic_residues
        )


class ECElementTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.ec = EC(
            self.field,
            self.field.gen_element(-4),
            self.field.gen_element(0)
        )

    def test_membership(self):
        self.ec.gen_element(self.field.gen_element(2), self.field.gen_element(0))

        with self.assertRaises(Exception):
            self.ec.gen_element(2, 1)

    def test_addition(self):
        p = self.ec.gen_element(2, 0)
        q = self.ec.gen_element(3, 46)
        expected = self.ec.gen_element(10, 14)

        self.assertEqual(p+q, expected)

        p = self.ec.gen_element(3, 46)
        q = self.ec.gen_element(3, 145)
        expected = self.ec.infinity
        self.assertEqual(p+q, expected)

    def test_multiplicaton(self):
        q = self.ec.gen_element(3, 46)
        expected = q + q
        self.assertEqual(q*2, expected)

        expected = q + q + q
        self.assertEqual(q*3, expected)

        expected = q + q + q + q
        self.assertEqual(q*4, expected)

        expected = q + q + q + q + q
        self.assertEqual(q*5, expected)

        expected = q + q + q + q + q + q
        self.assertEqual(q*6, expected)

        expected = q + q + q + q + q + q + q
        self.assertEqual(q*7, expected)

    def test_size_of_ec_group(self):
        self.field = ZModField(17)
        self.ec = EC.gen_from_int(self.field, 0, 7)

        elements = self.ec.generate_elements()
        logging.debug(sorted(elements))
        logging.debug(len(elements))

        for element in elements:
            logging.debug(f'{element}: {len(list(element.generate()))}, {list(element.generate())}')


class ECCTest(BaseTest):
    def setUp(self):
        """curve_secp256k1"""
        self.field = ZModField(2**256 - 2**32 - 977)
        self.ec = EC(
            field=self.field,
            a=self.field.gen_element(0),
            b=self.field.gen_element(7),
        )
        self.ecc = ECC(
            ec=self.ec,
            size=2**256 - 432420386565659656852420866394968145599,
            generator=self.ec.gen_element(
                55066263022277343669578718895168534326250603453777594175500187360389116729240,
                32670510020758816978083085130507043184471273380659243275938904335757337482424
            )
        )

    def test_signature_verification(self):
        private_key, public_key = self.ecc.generate_key_pair()
        message = b'foobar'
        signature = self.ecc.sign(message, private_key)

        self.assertTrue(self.ecc.verify(message, signature, public_key))

    def test_encryption(self):
        private_key, public_key = self.ecc.generate_key_pair()
        message = b'foobar'
        token, ephemeral_key = self.ecc.encrypt(message, public_key)
        self.assertEqual(message, self.ecc.decrypt(token, ephemeral_key, private_key))
