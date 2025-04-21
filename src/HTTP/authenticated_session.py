import requests, os, sys, traceback, threading, tempfile, atexit, time
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from socket import create_connection

class AuthSession(requests.Session):
    def __init__(self, cert_path: str = os.environ.get('CERT_PATH'), cert_pass: str = os.environ.get('CERT_PASS'), silent: bool = True) -> None:
        super().__init__()
        
        if silent: 
            import urllib3, warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            warnings.filterwarnings('ignore')
        
        try: create_connection(('8.8.8.8', 53), timeout=5)
        except: raise ConnectionError('No internet connection.')
        else:
            self.using: bool = True
            self.files = {}
            
            self.cert_thread = threading.Thread(target=self.keep_file, args=('cert',), daemon=True)
            self.key_thread = threading.Thread(target=self.keep_file, args=('key',), daemon=True)
            self.cert_thread.start()
            self.key_thread.start()
            
            while not self.files.get('cert') or not self.files.get('key'): pass
            
            self.verify = False
            self.cert = self.__authenticate(
                    cert_path=cert_path, 
                    cert_pass=cert_pass
            )
            
            atexit.register(self.__end)
        
    def __end(self):
        self.close()
        self.using = False
        self.cert_thread.join()
        self.key_thread.join()

        
    def keep_file(self, name: str):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
        temp_file.close()
        self.files[name] = temp_file.name
        
        while self.using:
            pass
    
        os.remove(temp_file.name)
    
    def __authenticate(self, cert_path: str, cert_pass: str) -> tuple[str, str]:
        """
        Convert .pfx certificate to .pem certificate and .pem key.
        
        :params
            cert_path: str - path to certificate file
            cert_pass: str - password in string format
        """
        try:
            if cert_path.endswith('.pem') and cert_pass.endswith('.pem'):
                return cert_path, cert_pass
            
            path: str = os.path.dirname(cert_path)
            
            with open(cert_path, 'rb') as f:
                pfx_data: bytes = f.read()
            
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(pfx_data, cert_pass.encode())
            
            key_path: str = self.files['key']
            cert_path: str = self.files['cert']

            with open(key_path, "wb") as key_file:
                key_file.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )

            with open(cert_path, "wb") as cert_file:
                cert_file.write(
                    certificate.public_bytes(
                        encoding=serialization.Encoding.PEM
                    )
                )

            if additional_certificates:
                chain_path: str = os.path.join(path, 'chain.pem')
                with open(chain_path, "wb") as chain_file:
                    for cert in additional_certificates:
                        chain_file.write(
                            cert.public_bytes(
                                encoding=serialization.Encoding.PEM
                            )
                        )

        except: 
            print('[Error] Authentication: Error converting digital certificate!')
            print(''.join(traceback.format_exception(*sys.exc_info())), '\n'*3)
            return None, None

        else:
            return cert_path, key_path

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    session: requests.Session = AuthSession(
        cert_path=os.environ.get('CERT_PATH'), 
        cert_pass=os.environ.get('CERT_PASS'),
        silent=True
    )
    print(session.get('https://www.google.com').status_code)
    
    time.sleep(3)
