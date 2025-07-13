import os
import json

class CertLoader:
    """
    Loads mTLS certificates from a Vault-injected file or environment variables.
    - Preferred: /vault/secrets/server_certs (injected as JSON)
    - Fallback: TLS_CRT, TLS_KEY, CA_CRT environment variables
    """

    def __init__(self, vault_path="/vault/secrets/server_certs"):
        self.vault_path = vault_path

    def load(self):
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
                print("✅ Loaded certs from Vault-injected file")
                return tls_crt, tls_key, ca_crt
        except Exception as e:
            raise Exception(f"❌ Failed to load certs from file: {e}")

    def _load_from_env(self):
        try:
            tls_crt = os.environ["TLS_CRT"].encode()
            tls_key = os.environ["TLS_KEY"].encode()
            ca_crt = os.environ["CA_CRT"].encode()
            print("✅ Loaded certs from environment variables")
            return tls_crt, tls_key, ca_crt
        except KeyError as e:
            raise Exception(f"❌ Missing environment variable: {e}")
