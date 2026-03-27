from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class AsymmetricCipher:
    """Provides RSA-based asymmetric encryption and decryption functionality using PKCS1_OAEP"""

    SIZE = 2048

    def __init__(self):
        """Generates a new RSA key pair and initializes the cipher with the private key"""
        self.private_key = RSA.generate(AsymmetricCipher.SIZE)
        self.public_key = self.private_key.public_key()
        self.cipher = PKCS1_OAEP.new(self.private_key)

    def get_public_key(self):
        """Exports and returns the public key in a format suitable for transmission"""
        return self.public_key.export_key()

    def decrypt(self, data: bytes):
        """Decrypts the provided byte data using the instance's private key"""
        return self.cipher.decrypt(data)

    @staticmethod
    def encrypt(public_key: str, data: bytes):
        """Encrypts data using a provided public key string for secure asymmetric transmission"""
        cipher = PKCS1_OAEP.new(RSA.importKey(public_key))
        return cipher.encrypt(data)