# --------------------------------------------------
# Imports

from socket import *
import re
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


# --------------------------------------------------
# Setup

reader = SimpleMFRC522()
GPIO.setwarnings(False)


def scan():
    while True:
        try:
            _, id = reader.read()
            break
        except:
            print('An error has occured \n')

    return id


# --------------------------------------------------
# Generate own private, public key pair

client_key = RSA.generate(1024)
client_private = client_key.export_key()
client_public = client_key.publickey().export_key()

file_out = open("client_private.pem", "wb")
file_out.write(client_private)
file_out.close()


# --------------------------------------------------
# Receive UDP broadcast from server

# Set up UDP socket
s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 12345))
m = s.recvfrom(3000)
string = m[0].decode('utf-8')

# Gather IP address and port from broadcast
ip = string[re.search("-----BEGIN IP-----", string).end()
                      :re.search("-----END IP-----", string).start()]
port = string[re.search("-----BEGIN PORT-----", string).end()
                        :re.search("-----END PORT-----", string).start()]

print("Connection details:")
print("    IP: ", ip)
print("    Port: ", port)
print()


# --------------------------------------------------
# Connect to server via TCP

# Set up TCP socket
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((ip, int(port)))

# Confirm that the user wants to connect
check = sock.recv(3000).decode('utf-8')
confirm = input(check)
print()

if confirm.upper() == 'Y':
    print('CONNECTION CONFIRMED')
elif confirm.upper() == 'N':
    print('CONNECTION CANCELLED')
else:
    print('INVALID INPUT, CONNECTION CANCELLED')

print()

sock.sendall(confirm.encode('utf-8'))


# --------------------------------------------------
# Authentication

# Receive public encryption key
key = sock.recv(3000)
print("Public key:")
print(key)
print()

# Write public key to .pem file
file_out = open("public.pem", "wb")
file_out.write(key)
file_out.close()

# Confirm receipt of public key with client public key
sock.sendall(client_public)

# Request password: Password
request = sock.recv(3000).decode('utf-8')
print(request)
print()

scan = scan().strip()
arr = scan.split('\n')
password = arr[-1]


# Encrypt password with public key and send
public = RSA.import_key(open("public.pem").read())
cipher_rsa = PKCS1_OAEP.new(public)
encrypted = cipher_rsa.encrypt(password.encode('utf-8'))
sock.sendall(encrypted)

# Access granted or denied
response = sock.recv(3000).decode('utf-8')
print(response)
print()

# Receive encrypted session key
session_encrypted = sock.recv(3000)
cipher_rsa = PKCS1_OAEP.new(client_key)
session_key = cipher_rsa.decrypt(session_encrypted)


print("Session key")
print(session_key)
print("Encrypted session key")
print(session_encrypted)
