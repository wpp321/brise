from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl.sm3 import sm3_hash
import base64


def sm4_encrypt(key, text):
    key = key.encode()
    text = text.encode()
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_ENCRYPT)
    encrypt_value = crypt_sm4.crypt_ecb(text)
    return (base64.b64encode(encrypt_value)).decode()


def sm4_decrypt(key, text):
    key = key.encode()
    text = base64.b64decode(text)
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_DECRYPT)
    encrypt_value = crypt_sm4.crypt_ecb(text)
    return encrypt_value.decode()


def sm4_encrypt_byte(key, content):
    key = key.encode()
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_ENCRYPT)
    encrypt_value = crypt_sm4.crypt_ecb(content)
    return encrypt_value


def sm4_decrypt_byte(key, content):
    key = key.encode()
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_DECRYPT)
    encrypt_value = crypt_sm4.crypt_ecb(content)
    return encrypt_value


def sm3(text):
    return sm3_hash(list(text.encode()))


def sm3_byte(binary):
    return sm3_hash(list(binary))
