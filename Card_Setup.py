from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()
GPIO.setwarnings(False)

print('SET UP NEW USER')

last = input('    Last name: ')
first = input('    First name: ')
userid = input('    User ID: ')
password = input('    Password: ')

data = f'''
{last}
{first}
{userid}
{password}
'''

print('Scan now')
try:
    reader.write(data)
    print("Written")

except Exception as e:
    print(e)
