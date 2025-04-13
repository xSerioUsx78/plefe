import json
from django.conf import settings
from cryptography.fernet import Fernet


FERNET_KEY = getattr(settings, 'FERNET_ENCRYPT_KEY')

DEFAULT_ENDCODE_DECODE = 'utf-8'

def fernet_encrypt(string) -> str:
    fernet = Fernet(FERNET_KEY)
    encrypted = fernet.encrypt(string.encode())
    return encrypted.decode(DEFAULT_ENDCODE_DECODE)


def fernet_decrypt(string) -> str:
    fernet = Fernet(FERNET_KEY)
    decrypted = fernet.decrypt(
        bytes(string, DEFAULT_ENDCODE_DECODE)
    )
    return decrypted.decode(DEFAULT_ENDCODE_DECODE)


def open_json_file(path):
    with open(path, 'r') as file:
        json_file = json.load(file)
        return json_file


def write_json_file(path, obj, indent=2):
    with open(path, 'w') as file:
        json.dump(obj, file, indent=indent)