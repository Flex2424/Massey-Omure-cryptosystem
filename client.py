import socket
import gmpy2
from random import randint
from os import urandom
from Crypto.Cipher import DES

import asn1


def parse_file(filename, mylist):
    with open(filename, 'rb') as file:
        data = file.read()
    file = asn1.Decoder()
    file.start(data)
    parsing_file(file, mylist)


def parsing_file(file, mylist):
    while not file.eof():
        try:
            tag = file.peek()
            if tag.nr == asn1.Numbers.Null:
                break
            if tag.typ == asn1.Types.Primitive:
                tag, value = file.read()
                if tag.nr == asn1.Numbers.Integer:
                    mylist.append(value)
            else:
                file.enter()
                parsing_file(file, mylist)
                file.leave()
        except asn1.Error:
            break


def encrypt_triple_des(key):
    cipher_text = bytes()
    des = DES.new(key, DES.MODE_ECB)
    with open('input', 'r') as file:
        data = file.read()
        to_add = 0
        if len(data) % 8 != 0:
            to_add = 8 - len(data) % 8
        data += ' ' * to_add
        cipher_text = des.encrypt(data)
        return cipher_text

p = gmpy2.next_prime(randint(50000, 500000))
r = p - 1
t = 15394852587444895931

decoded_values = []
decoded_values_2 = []

while True:
    a = gmpy2.next_prime(randint(50000, 500000))
    if gmpy2.invert(a, r) != 0:
        break

print('\n[+] Generated a..')
# self.t = int.from_bytes(self._t, byteorder='big')
t %= p
key = int(t).to_bytes(8, byteorder='big')
cipher_text = encrypt_triple_des(key)
with open('cipher', 'wb') as c:
    c.write(cipher_text)
ta = gmpy2.powmod(t, a, p)
print('\n[+] Calculated t^a')

asn = asn1.Encoder()
asn.start()
asn.enter(asn1.Numbers.Sequence)
asn.write(p, asn1.Numbers.Integer)
asn.write(r, asn1.Numbers.Integer)
asn.leave()

asn.enter(asn1.Numbers.Sequence)
asn.write(ta, asn1.Numbers.Integer)
asn.leave()

asn.enter(asn1.Numbers.Sequence)
asn.enter(asn1.Numbers.Set)
asn.enter(asn1.Numbers.Sequence)
asn.write(b'\x80\x07\x02\x00', asn1.Numbers.OctetString)
asn.write(b'mo', asn1.Numbers.UTF8String)
asn.enter(asn1.Numbers.Sequence)
asn.leave()
asn.enter(asn1.Numbers.Sequence)
asn.write(p, asn1.Numbers.Integer)
asn.write(r, asn1.Numbers.Integer)
asn.leave()
asn.leave()

asn.enter(asn1.Numbers.Sequence)
asn.write(ta, asn1.Numbers.Integer)
asn.leave()
asn.leave()
asn.leave()
asn.enter(asn1.Numbers.Sequence)
asn.leave()
# asn.leave()
out = asn.output()
with open('step1', 'wb') as file:
    file.write(out)

sock = socket.socket()
sock.connect(('localhost', 9090))
sock.send(out)
print('\n[+]Sending data to server..')
data = sock.recv(1024)
with open('received_step_2', 'wb') as file:
    file.write(data)

parse_file('received_step_2', decoded_values)
print('\n[+] Received t^ab')
tab = decoded_values[0]
reverse_a = gmpy2.invert(a, r)
tb = gmpy2.powmod(tab, reverse_a, p)
print('\n[+] Calc t^ab^a^(-1)')
file3 = asn1.Encoder()
file3.start()
file3.enter(asn1.Numbers.Sequence)
file3.enter(asn1.Numbers.Set)
file3.enter(asn1.Numbers.Sequence)
file3.write(b'\x80\x07\x02\x00', asn1.Numbers.OctetString)
file3.write(b'mo', asn1.Numbers.UTF8String)
file3.enter(asn1.Numbers.Sequence)
file3.leave()

file3.enter(asn1.Numbers.Sequence)
file3.leave()

file3.enter(asn1.Numbers.Sequence)
file3.write(tb, asn1.Numbers.Integer)
file3.leave()
file3.leave()
file3.leave()

file3.enter(asn1.Numbers.Sequence)
file3.write(b'\x01\x21', asn1.Numbers.OctetString)
file3.write(len(cipher_text), asn1.Numbers.Integer)
file3.leave()
file3.leave()
file3.write(cipher_text)
encoded_bytes3 = file3.output()
with open('step3', 'wb') as f3:
    f3.write(encoded_bytes3)

sock.send(encoded_bytes3)
print('\n[+] Done!')



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
