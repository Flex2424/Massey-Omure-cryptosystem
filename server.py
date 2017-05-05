import socket
import gmpy2
from random import randint
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

decoded_values = []
decoded_values_2 = []

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)
conn, addr = sock.accept()
print('[+] Connected from: ', addr)
data = conn.recv(1024)
if len(data):
    print('\n[+] Received first ASN-struct from client')
    print('[+] Saved as "received_step1"')
with open('received_step1', 'wb') as file:
    file.write(data)

parse_file('received_step1', decoded_values)


ta = decoded_values[2]
r = decoded_values[1]
p = decoded_values[0]
print('\n[+] Received p, r, t^a')

while True:
    b = gmpy2.next_prime(randint(50000, 500000))
    if gmpy2.invert(b, r) != 0:
        break
print('\n[+] Generated b..')
tab = gmpy2.powmod(ta, b, p)
print('\n[+] Making b^a..')

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
print('\n[+] Sendind data to client...')
conn.send(encoded_bytes2)

data = conn.recv(1024)
if len(data):
    print('\n[+] Received new ASN-struct from client')
    print('[+] Saved as "received_step3"')
with open('received_step3', 'wb') as file:
    file.write(data)

parse_file('received_step3', decoded_values_2)

tb = decoded_values_2[0]
reverse_b = gmpy2.invert(b, r)
new_t = int(gmpy2.powmod(tb, reverse_b, p))
print('\n[+] Calculated (t^b)^b^(-1)')
new_t %= 2 ** 64
print(new_t)
key = new_t.to_bytes(8, byteorder='big')
# key = t.to_bytes(8, byteorder='big')

decrypted_text = bytes()
des = DES.new(key, DES.MODE_ECB)
with open('cipher', 'rb') as file:
    while True:
        block = file.read(DES.block_size)
        if len(block) == 0:
            break
        if len(block) % DES.block_size != 0:
            block += b'\x03' * (DES.block_size - len(block) % DES.block_size)
        decrypted_text += des.decrypt(block)

print('\n[+]Decrypted text:')
print(decrypted_text.decode('utf-8', 'ignore'))





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
