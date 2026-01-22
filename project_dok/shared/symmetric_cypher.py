from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class SymmetricCipher:
    SYMMETRIC_KEY_SIZE = 32
    IV_SIZE = 16
    MODE = AES.MODE_CFB

    def __init__(self, symmetric_key: bytes, iv: bytes):
        self.key = symmetric_key
        self.iv = iv

    def encrypt(self, data: bytes) -> bytes:
        """encrypt - msg"""
        cipher = AES.new(self.key, self.MODE, iv=self.iv)
        return cipher.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        """decrypt - msg"""
        cipher = AES.new(self.key, self.MODE, iv=self.iv)
        return cipher.decrypt(data)

    @staticmethod
    def random_symmetric_key():
        """get random key"""
        return get_random_bytes(SymmetricCipher.SYMMETRIC_KEY_SIZE)

    @staticmethod
    def random_iv():
        """get iv - 16 random byte"""
        return get_random_bytes(SymmetricCipher.IV_SIZE)