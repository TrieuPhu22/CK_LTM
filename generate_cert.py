from datetime import datetime, timedelta
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Tạo private key
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Thông tin chứng chỉ
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"VN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"HCM"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Ho Chi Minh City"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Football Hub"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

# Thêm các Subject Alternative Names
san = [
    x509.DNSName("localhost"),
    x509.DNSName("127.0.0.1"),
    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))
]

# Tạo chứng chỉ
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.utcnow()
).not_valid_after(
    datetime.utcnow() + timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName(san),
    critical=False,
).add_extension(
    x509.BasicConstraints(ca=False, path_length=None),
    critical=True,
).sign(key, hashes.SHA256())

# Ghi ra file
with open("key.pem", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Chứng chỉ SSL đã được tạo thành công: cert.pem và key.pem")