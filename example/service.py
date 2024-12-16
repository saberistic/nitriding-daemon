from flask import Flask
import time
import urllib.request

app = Flask(__name__)

nitriding_url = "http://127.0.0.1:8080/enclave/ready"


@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About page'

@app.route('/attestation')
def enclave_ready():
    r = urllib.request.urlopen(nitriding_url)
    if r.getcode() != 200:
        return 'Enclave not ready'
    else:
        return 'Enclave ready'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7047)
