from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes


class SymmetricCipher:

    SYMMETRIC_KEY_SIZE = 24
    IV_SIZE = 8
    MODE = DES3.MODE_CFB

    def __init__(self, symmetric_key: bytes, iv: bytes):
        self.key = symmetric_key
        self.iv = iv

    def encrypt(self, data: bytes):
        """
        Encrypts the given data using the triple DES cipher.

        :param data: Input data to be encrypted.
        :return: Encrypted data.
        """
        encrypt_cipher = DES3.new(self.key, SymmetricCipher.MODE, iv=self.iv)
        return encrypt_cipher.encrypt(data)

    def decrypt(self, data: bytes):
        """
        Decrypts given data using the cipher instance.

        :param data: Encrypted data as bytes
        :return: Decrypted data as bytes
        """
        decrypt_cipher = DES3.new(self.key, SymmetricCipher.MODE, iv=self.iv)
        return decrypt_cipher.decrypt(data)

    @staticmethod
    def random_symmetric_key():
        """
        Return random bytes that can be used as a symmetric key.

        :return: bytes
        """
        key = get_random_bytes(SymmetricCipher.SYMMETRIC_KEY_SIZE)
        while True:
            try:
                key = DES3.adjust_key_parity(key)
                break
            except ValueError:
                # If the key is invalid, regenerate
                key = get_random_bytes(SymmetricCipher.SYMMETRIC_KEY_SIZE)

        return key

    @staticmethod
    def random_iv():
        return get_random_bytes(SymmetricCipher.IV_SIZE)
