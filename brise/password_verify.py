from .sm_util import *

key = "hipp5q49dlc5hsiq"


def password_en(p):
    return sm4_encrypt(key, p)


def password_de(p):
    return sm4_decrypt(key, p)
