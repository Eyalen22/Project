from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class SymmetricCipher:
    SYMMETRIC_KEY_SIZE = 32
    IV_SIZE = 16
    MODE = AES.MODE_CFB

    def __init__(self, symmetric_key: bytes, iv: bytes):
        self.key = symmetric_key
        self.iv = iv

    def get_fresh_cipher(self):
        """יוצרת אובייקט AES רענן שמתחיל מתחילת הזרם - קריטי לסנכרון קבצים"""
        return AES.new(self.key, self.MODE, iv=self.iv)

    def encrypt(self, data: bytes) -> bytes:
        """הצפנה רגילה להודעות קצרות"""
        cipher = self.get_fresh_cipher()
        return cipher.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        """פענוח רגיל להודעות קצרות"""
        cipher = self.get_fresh_cipher()
        return cipher.decrypt(data)

    @staticmethod
    def random_symmetric_key():
        """get random key"""
        return get_random_bytes(SymmetricCipher.SYMMETRIC_KEY_SIZE)

    @staticmethod
    def random_iv():
        """get iv - 16 random byte"""
        return get_random_bytes(SymmetricCipher.IV_SIZE)