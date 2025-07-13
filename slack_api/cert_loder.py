import os
import json

class CertLoader:
    """
    CertLoader fetches TLS certificate, key, and CA cert needed for mutual TLS (mTLS)
    using the following priority:
    1. Vault-injected JSON file at /vault/secrets/server_certs
    2. Environment variables: TLS_CRT, TLS_KEY, CA_CRT
    """

    def __init__(self, vault_path="/vault/secrets/server_certs"):
        self.vault_path = vault_path

    def load(self):
        """
        Returns:
            tuple: (tls_crt: bytes, tls_key: bytes, ca_crt: bytes)

        Raises:
            Exception if certs cannot be loaded from either source.
        """
        if os.path.exists(self.vault_path):
            return self._load_from_file()
        else:
            return self._load_from_env()

    def _load_from_file(self):
        try:
            with open(self.vault_path, "r") as f:
                data = json.load(f)
                tls_crt = data["tls.crt"].encode()
                tls_key = data["tls.key"].encode()
                ca_crt = data["ca.crt"].encode()
                print("✅ Loaded certs from Vault-injected file:", self.vault_path)
                return tls_crt, tls_key, ca_crt
        except Exception as e:
            raise Exception(f"❌ Failed to load certs from {self.vault_path}: {e}")

    def _load_from_env(self):
        try:
            tls_crt = os.environ["TLS_CRT"].encode()
            tls_key = os.environ["TLS_KEY"].encode()
            ca_crt = os.environ["CA_CRT"].encode()
            print("✅ Loaded certs from environment variables")
            return tls_crt, tls_key, ca_crt
        except KeyError as e:
            raise Exception(f"❌ Missing environment variable: {e}")
