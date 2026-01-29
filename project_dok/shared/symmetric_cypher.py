from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib

class SymmetricCipher:

    SYMMETRIC_KEY_SIZE = 32
    MODE = AES.MODE_CFB

    def __init__(self, symmetric_key: bytes):
        self.key = symmetric_key
        self.generated_iv = hashlib.sha256(self.key).digest()[:16]

    def encrypt(self, data: bytes):
        """
        Encrypts the given data using the AES cipher.
        """
        encrypt_cipher = AES.new(self.key, SymmetricCipher.MODE, iv=self.generated_iv)
        return encrypt_cipher.encrypt(data)

    def decrypt(self, data: bytes):
        """
        Decrypts given data using the AES cipher instance.
        """
        encrypt_cipher = AES.new(self.key, SymmetricCipher.MODE, iv=self.generated_iv)
        return encrypt_cipher.decrypt(data)

    @staticmethod
    def random_symmetric_key():
        """
        Return random bytes that can be used as an AES symmetric key.
        """
        return get_random_bytes(SymmetricCipher.SYMMETRIC_KEY_SIZE)


if __name__ == '__main__':
    key = SymmetricCipher.random_symmetric_key()
    mySYm = SymmetricCipher(key)
    msg = 'hello world'
    enc_msg = mySYm.encrypt(msg.encode())

    mySym2 = SymmetricCipher(key)
    bb = mySym2.decrypt(enc_msg).decode()
    print(bb)

