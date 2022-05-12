# Networking_Final_Project
Final project for Networking CSCI420A - authentication system over TCP.

This project is an attempt at designing an authentication system in Python. Using public and private encryption keys, a secure connection is established between the client and server and a shared session key is transmitted; key generation and encryption are handled by the PyCryptodome library. The user's identity is verified using an RFID card, rather than by a typed password. For this we use a MFRC522 RFID scanner connected to a Rasperry Pi, and the ```SimpleMFRC522``` library. The system runs primarily over a TCP connection, which is implemented using the ```socket``` module.

### Authentication Protocol
1. The Server generates a public and private key
2. Over UDP, the Server broadcasts its IP address and the TCP port designated for the secure connection; the Server then listens for connections on the TCP socket
3. The Client receives the UDP broadcast and establishes a TCP connection using the advertized information
4. The Server sends its public encryption key over the TCP connection; the Client saves this key
5. As an acknowledgement, the Client sends its own public encryption key over the connection; the Server saves this key
6. The Server requests verification of the user's identity
7. The RFID card is scanned on the client side; the data is encrypted using the Server's public key and transmitted
8. The Server decrypts the RFID data and reads the ```password``` field
9. The password is run through a hash function and compared the the existing password hash; access is granted to the Client if the hashes match
10. Once access is granted, the Server generates a session key; this is encrypted using the Client's public key and transmitted
11. The Client decrypts the session key; it can now be used to encrypt transmissions for the rest of the session

### Files
```Card_Setup.py``` is used to write user information to an RFID card in the correct format. RFID cards should be set up prior to running either of the two other files.

```Client_Final.py``` runs on the client (represented in our case by the Raspberry Pi). This file should be run before ```Server_Final.py```.

```Server_Final.py``` runs on the server (represented in our case by a laptop).

