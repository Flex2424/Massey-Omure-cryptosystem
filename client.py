import socket
import gmpy2
from random import randint
from os import urandom

import asn1


class MasseyOmureClient:
    def __init__(self):
        self.p = gmpy2.next_prime(randint(50000, 500000))
        self.r = self.p - 1
        self._t = urandom(24)

        while True:
            self.a = gmpy2.next_prime(randint(50000, 500000))
            if gmpy2.invert(self.a, self.r) != 0:
                break
        self.t = int.from_bytes(self._t, byteorder='big')
        self.t %= self.p
        self.ta = gmpy2.powmod(self.t, self.a, self.p)

        self.sock = socket.socket()

    def making_step_one(self):
        asn = asn1.Encoder()
        asn.start()
        asn.enter(asn1.Numbers.Sequence)
        asn.write(self.p, asn1.Numbers.Integer)
        asn.write(self.r, asn1.Numbers.Integer)
        asn.leave()

        asn.enter(asn1.Numbers.Sequence)
        asn.write(self.ta, asn1.Numbers.Integer)
        asn.leave()

        asn.enter(asn1.Numbers.Sequence)
        asn.enter(asn1.Numbers.Set)
        asn.enter(asn1.Numbers.Sequence)
        asn.write(b'\x80\x07\x02\x00', asn1.Numbers.OctetString)
        asn.write(b'mo', asn1.Numbers.UTF8String)
        asn.enter(asn1.Numbers.Sequence)
        asn.leave()
        asn.enter(asn1.Numbers.Sequence)
        asn.write(self.p, asn1.Numbers.Integer)
        asn.write(self.r, asn1.Numbers.Integer)
        asn.leave()
        asn.leave()

        asn.enter(asn1.Numbers.Sequence)
        asn.write(self.ta, asn1.Numbers.Integer)
        asn.leave()
        asn.leave()
        asn.leave()
        asn.enter(asn1.Numbers.Sequence)
        asn.leave()
        asn.leave()
        return asn.output()

    def send_step_one(self, encoded_bytes):
        self.sock.connect(('localhost', 9090))
        self.sock.send(encoded_bytes)




# STEP 1
# p = gmpy2.next_prime(randint(50000, 500000))
# r = p - 1
# t = urandom(24)

# while True:
#     a = gmpy2.next_prime(randint(50000, 500000))
#     if gmpy2.invert(a, r) != 0:
#         break

# t_int = int.from_bytes(t, byteorder='big')
#
# t_int = t_int % p
# ta = gmpy2.powmod(t_int, a, p)

# sock = socket.socket()
# sock.connect(('localhost', 9090))
# sock.send(b'hello, world!')
#
# data = sock.recv(1024)
# sock.close()

# print(data)
