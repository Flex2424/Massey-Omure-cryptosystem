import socket
import gmpy2
from random import randint
from os import urandom

import asn1


class MasseyOmureServer:
    def __init__(self):
        self.p = 0
        self.r = 0
        self.b = 0
        self.t = 0

        self.sock = socket.socket()
        self.conn = None
        self.addr = None

        self.decoded_values = []
        self.decoded_values_2 = []

    def making_step_two(self):
        self.sock.bind(('', 9090))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        print('[+] Connected from: ', self.addr)
        data = self.conn.recv(1024)
        with open('received_step1', 'wb') as file:
            file.write(data)

        self.parse_data('received_step1')

    def parse_file(self, filename, mylist):
        with open(filename, 'rb') as file:
            data = file.read()
        file = asn1.Decoder()
        file.start(data)
        self.parsing_file(file, mylist)

    def parsing_file(self, file, mylist):
        while not file.eof():
            try:
                tag = file.peek()
                if tag.nr == asn1.Numbers.Null:
                    break
                if tag.typ == asn1.Types.Primitive:
                    tag, value = file.read()
                    if tag.nr == asn1.Numbers.Integer:
                        self.mylist.append(value)
                else:
                    file.enter()
                    self.parsing_file(file, mylist)
                    file.leave()
            except asn1.Error:
                break

    def making_step_two(self):
        ta = self.decoded_values[2]
        r = self.decoded_values[1]
        p = self.decoded_values[0]

        while True:
            self.b = gmpy2.next_prime(randint(50000, 500000))
            if gmpy2.invert(self.b, r) != 0:
                break

        tab = gmpy2.powmod(ta, self.b, p)

        file2 = asn1.Encoder()
        file2.start()
        file2.enter(asn1.Numbers.Sequence)
        file2.enter(asn1.Numbers.Set)
        file2.enter(asn1.Numbers.Sequence)
        file2.write(b'\x80\x07\x02\x00', asn1.Numbers.OctetString)
        file2.write(b'mo', asn1.Numbers.UTF8String)
        file2.enter(asn1.Numbers.Sequence)
        file2.leave()

        file2.enter(asn1.Numbers.Sequence)
        file2.leave()

        file2.enter(asn1.Numbers.Sequence)
        file2.write(tab, asn1.Numbers.Integer)
        file2.leave()
        file2.leave()
        file2.leave()

        file2.enter(asn1.Numbers.Sequence)
        file2.leave()
        file2.leave()
        encoded_bytes2 = file2.output()
        with open('step2', 'wb') as f:
            f.write(encoded_bytes2)

        self.conn.send(encoded_bytes2)





# sock = socket.socket()
# sock.bind(('', 9090))
# sock.listen(1)
# conn, addr = sock.accept()
#
# print('connected:', addr)
#
# while True:
#     data = conn.recv(1024)
#     if not data:
#         break
#     conn.send(data.upper())
#
# conn.close()
