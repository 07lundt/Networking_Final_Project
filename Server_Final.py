#!/usr/bin/env python

# --------------------------------------------------
# Imports

from socket import *
import pandas as pd
import socket
import numpy as np
from time import sleep
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import bcrypt


# --------------------------------------------------
# Stored password hash and salt

hash = b'$2b$12$k/Obmcgc3s3roBuCVQYFgu/uPxOn2SVNlGn7IBdm8H/SOHf4xwct6'
salt = b'$2b$12$k/Obmcgc3s3roBuCVQYFgu'


# --------------------------------------------------
# Generate private, public key pair

key = RSA.generate(1024)
private_key = key.export_key()
public_key = key.publickey().export_key()

file_out = open("private.pem", "wb")
file_out.write(private_key)
file_out.close()

print("KEY GENERATED")
print()


# --------------------------------------------------
# UDP broadcast, TCP connection

udp = socket.socket(AF_INET, SOCK_DGRAM)
udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

ip = gethostbyname(gethostname())
TCP_PORT = np.random.randint(5000, 5010)

tcp = socket.socket(AF_INET, SOCK_STREAM)
tcp.bind((ip, TCP_PORT))

broadcast = f'''
-----BEGIN IP-----{ip}-----END IP-----
-----BEGIN PORT-----{TCP_PORT}-----END PORT-----
'''
udp.sendto(broadcast.encode('utf-8'), ('255.255.255.255', 12345))

tcp.listen()

conn, addr = tcp.accept()

# Confirm client connection to server
conn.sendall("CONNECTING TO LAB, CONTINUE? [y/n] ".encode('utf-8'))

confirm = conn.recv(3000).decode('utf-8')
if confirm.upper() == 'Y':
    print("CONNECTION CONFIRMED")
    print()
else:
    print("CONNECTION CANCELLED")
    print()
    conn.close()
    tcp.close()

# Send public key, receive client public key
conn.sendall(public_key)

client_public = conn.recv(3000)
print("CLIENT PUBLIC KEY: ", client_public)
print()

# Write client public key to .pem file
file_out = open("client_public.pem", "wb")
file_out.write(client_public)
file_out.close()

# Request password
conn.sendall("SCAN CARD NOW".encode('utf-8'))

encrypted = conn.recv(3000)
cipher_rsa = PKCS1_OAEP.new(key)
password = cipher_rsa.decrypt(encrypted)

# Compare hashed password and stored hash
print("Hashed password: ", bcrypt.hashpw(password, salt))
print("Stored hash: ", hash)
print()

if bcrypt.hashpw(password, salt) == hash:
    conn.sendall("ACCESS GRANTED".encode('utf-8'))
else:
    conn.sendall("INCORRECT PASSWORD, ACCESS DENIED".encode('utf-8'))
    conn.close()
    tcp.close()

# Generate and encrypt session key
session_key = get_random_bytes(16)

client_public = RSA.import_key(open("client_public.pem").read())
cipher_rsa = PKCS1_OAEP.new(client_public)
session_encrypted = cipher_rsa.encrypt(session_key)

conn.sendall(session_encrypted)

print("Session key")
print(session_key)
print("Encrypted session key")
print(session_encrypted)
