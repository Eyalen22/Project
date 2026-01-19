from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class AsymmetricCipher:

    SIZE = 2048

    def __init__(self):
        self.private_key = RSA.generate(AsymmetricCipher.SIZE)
        self.public_key = self.private_key.public_key()
        self.cipher = PKCS1_OAEP.new(self.private_key)

    def get_public_key(self):
        return self.public_key.export_key()

    def decrypt(self, data: bytes):
        return self.cipher.decrypt(data)

    @staticmethod
    def encrypt(public_key: str, data: bytes):
        cipher = PKCS1_OAEP.new(RSA.importKey(public_key))
        return cipher.encrypt(data)