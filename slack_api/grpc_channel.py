import grpc
from cert_loader import CertLoader

def create_secure_channel(grpc_target: str) -> grpc.Channel:
    """
    Creates a secure gRPC channel with mTLS using certs from CertLoader.
    
    Args:
        grpc_target (str): The gRPC server address, e.g. 'my-grpc.service:443'

    Returns:
        grpc.Channel: A secure gRPC channel
    """
    tls_crt, tls_key, ca_crt = CertLoader().load()

    creds = grpc.ssl_channel_credentials(
        root_certificates=ca_crt,
        private_key=tls_key,
        certificate_chain=tls_crt
    )

    return grpc.secure_channel(grpc_target, creds)
