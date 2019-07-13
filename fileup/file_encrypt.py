from cryptography.fernet import Fernet
from .settings import ENCRYPT_KEY


def encryptFile(path):
    """
    Takes in the path of the file that needs be encrypted. The file is overwritten with the encrypted version.
    (Only encrypted files are stored)
    """
    with open(path, 'rb') as f:
        data = f.read()

    fernet = Fernet(ENCRYPT_KEY)
    encrypted = fernet.encrypt(data)

    with open(path, 'wb') as f:
        f.write(encrypted)


def decryptFile(path):
    """    
    Creates a temp path where the encrypted file would be copied and decrypted.
    Returns temp path

    ** delete decrypted file after use.
    ** function returns the temp path
    """
    with open(path, 'rb') as f:
        data = f.read()

    fernet = Fernet(ENCRYPT_KEY)
    decrypted = fernet.decrypt(data)

    #TODO Create a temp path for the file/or no path at all. Just return data        
    with open(path, 'wb') as f:
        f.write(decrypted)

