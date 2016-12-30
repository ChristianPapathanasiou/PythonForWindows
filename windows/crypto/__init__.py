from windows.generated_def import X509_ASN_ENCODING, PKCS_7_ASN_ENCODING

DEFAULT_ENCODING = X509_ASN_ENCODING | PKCS_7_ASN_ENCODING
# Keep other import here so sub-crypto file can import windows.crypto.DEFAULT_ENCODING
from windows.crypto.certificate import *
from windows.crypto.encrypt_decrypt import *
