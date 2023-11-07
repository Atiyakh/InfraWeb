from Crypto.Cipher import AES, PKCS1_v1_5
from hashlib import sha512, sha256, sha1
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime, base64, os, hashlib

def Encode(data):
    if isinstance(data, str): return data.encode('utf-8')
    else: return data

class Hash:
    Sha1 = lambda plain_text: hashlib.sha1(Encode(plain_text)).hexdigest()
    Sha224 = lambda plain_text: hashlib.sha224(Encode(plain_text)).hexdigest()
    Sha384 = lambda plain_text: hashlib.sha384(Encode(plain_text)).hexdigest()
    Sha256 = lambda plain_text: hashlib.sha256(Encode(plain_text)).hexdigest()
    Sha512 = lambda plain_text: hashlib.sha512(Encode(plain_text)).hexdigest()
    Scrypt = lambda plain_text, n, r, p, salt=b'AuKlYusS4TsL': hashlib.scrypt(plain_text, salt=salt, n=n, r=r, p=p)

directory = Path(__file__).resolve().parent

def generateSSLPrivateKey_Certificate():
    # RSA key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
    # self signed certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u'localhost')]),
        critical=False
    ).sign(private_key, hashes.SHA256(), default_backend())

    with open(os.path.join(directory, r'Certificates\server_private_key.pem'), 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(os.path.join(directory, r'Certificates\ssl_tls_certificate.pem'), 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

class Hashing_Algorithms:
    def Sha512(self, text:str):
        bytes_ = sha512(text.encode('utf-8'))
        hash = bytes_.hexdigest()
        return hash

    def Sha256(self, text):
        bytes_ = sha256(text.encode('utf-8'))
        hash = bytes_.hexdigest()
        return hash

    def Sha1(self, text):
        bytes_ = sha1(text.encode('utf-8'))
        hash = bytes_.hexdigest()
        return hash

class AES_Algorithm:
    def Encrypt(self, data):
        block_size = 16
        padding = b"*"
        p = lambda s:s + (block_size-len(s)%block_size)*padding
        KEY = Random.new().read(16)
        IV = Random.new().read(16)
        E = AES.new(KEY, AES.MODE_CBC, IV)
        Encrypted_message = base64.b64encode(IV+ E.encrypt(p(data)))
        return Encrypted_message, KEY

    def Decrypt(self, KEY, Encrypted_message):
        Encrypted_Data = base64.b64decode(Encrypted_message)
        IV_ = Encrypted_Data[:16]
        Encrypted_message_ = Encrypted_Data[16:]
        print(len(IV_), len(Encrypted_message_))
        D = AES.new(KEY, AES.MODE_CBC, IV_)
        plain_text = D.decrypt(Encrypted_message_).rstrip(b"*")
        return plain_text

class RSA_Algorithm:
    def slice(self, data, num):
        d = [data[num*i:num*(i+1)] for i in range(int(len(data)/num))]
        completance = [data[num*int(len(data)/num):]]
        if completance not in [[''], [b''], []]: d += completance
        return d

    def generateKeys(self):
        key = RSA.generate(2048)
        private_key = key.exportKey()
        public_key = key.publickey().exportKey()
        return public_key, private_key
    
    def encrypt(self, plain_text, public_key):
        loaded_key1 = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(loaded_key1)
        plain_list = self.slice(plain_text, 245)
        cipher_list = [base64.b64encode(cipher.encrypt(i)) for i in plain_list]
        return b''.join(cipher_list)
    
    def decrypt(self, cipher_text, private_key):
        loaded_key = RSA.importKey(private_key)
        cipher = PKCS1_v1_5.new(loaded_key)
        n = Random.new().read(int(15/SHA.digest_size))
        cipher_list = self.slice(cipher_text, 344)
        plain_list = [cipher.decrypt(base64.b64decode(i), n) for i in cipher_list]
        return b''.join(plain_list)

class Crytography:
    def __init__(self):
        self.AES = AES_Algorithm()
        self.RSA = RSA_Algorithm()
        self.Hash = Hashing_Algorithms()
