from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

BASE_DIR = Path(__file__).resolve().parent
CERTS_DIR = BASE_DIR / "certs"
ISSUED_DIR = CERTS_DIR / "issued"
CA_KEY_PATH = CERTS_DIR / "ca.key"
CA_CERT_PATH = CERTS_DIR / "ca.crt"


# Returns the user's certificate if it exists, otherwise creates a new one.
def get_or_issue_user_certificate(username: str) -> bytes:
    ensure_ca_exists()

    cert_path = ISSUED_DIR / f"{username}.crt"
    if cert_path.exists():
        return cert_path.read_bytes()

    return issue_user_certificate(username)


# Creates the needed folders for storing certificates.
def _ensure_dirs():
    CERTS_DIR.mkdir(parents=True, exist_ok=True)
    ISSUED_DIR.mkdir(parents=True, exist_ok=True)


# Creates a local CA certificate and key if they do not exist yet.
def ensure_ca_exists() -> None:
    _ensure_dirs()
    if CA_KEY_PATH.exists() and CA_CERT_PATH.exists():
        return

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IL"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CyberSecurityProject-LocalCA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Local CA"),
    ])

    now = datetime.now(timezone.utc)

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )

    CA_KEY_PATH.write_bytes(
        ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    )
    CA_CERT_PATH.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))


# Creates and saves a new client certificate for the given username, signed by the local CA.
def issue_user_certificate(username: str) -> bytes:
    ensure_ca_exists()

    ca_key = serialization.load_pem_private_key(CA_KEY_PATH.read_bytes(), password=None)
    ca_cert = x509.load_pem_x509_certificate(CA_CERT_PATH.read_bytes())

    user_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CyberSecurityProject"),
        x509.NameAttribute(NameOID.COMMON_NAME, username),
    ])

    now = datetime.now(timezone.utc)

    user_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(user_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False
        )
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )

    cert_pem = user_cert.public_bytes(serialization.Encoding.PEM)

    out_path = ISSUED_DIR / f"{username}.crt"
    out_path.write_bytes(cert_pem)

    return cert_pem


# Returns the CA certificate so clients can trust certificates signed by it.
def get_ca_certificate_pem() -> bytes:
    ensure_ca_exists()
    return CA_CERT_PATH.read_bytes()
