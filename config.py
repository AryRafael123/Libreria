import os
import binascii

# config.py
class Config:
    secretKey = binascii.hexlify(os.urandom(24)).decode()
