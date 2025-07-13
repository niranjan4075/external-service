import grpc
import json

def load_cert_from_vault_json():
    try:
        with open("/vault/secrets/server_certs", "r") as f:
            data = json.load(f)
            tls_crt = data["tls.crt"].encode()
            tls_key = data["tls.key"].encode()
            ca_crt = data["ca.crt"].encode()
            print("✅ Loaded mTLS certs from /vault/secrets/server_certs")
            return tls_crt, tls_key, ca_crt
    except Exception as e:
        print(f"❌ Failed to load certs from Vault file: {e}")
        raise

def create_secure_channel():
    tls_crt, tls_key, ca_crt = load_cert_from_vault_json()

    creds = grpc.ssl_channel_credentials(
        root_certificates=ca_crt,
        private_key=tls_key,
        certificate_chain=tls_crt
    )

    return grpc.secure_channel("your.grpc.server:443", creds)

def run():
    channel = create_secure_channel()
    stub = YourGrpcStub(channel)  # Replace this with your generated stub
    # Call Encrypt / Decrypt methods here

if __name__ == "__main__":
    run()
