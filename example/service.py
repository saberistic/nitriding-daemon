from flask import Flask
import time
import urllib.request
import anthropic

app = Flask(__name__)

nitriding_url = "http://127.0.0.1:8080/enclave"

def signal_ready():
    r = urllib.request.urlopen(nitriding_url + "/ready")
    if r.getcode() != 200:
        raise Exception("Expected status code %d but got %d" %
                        (requests.status_codes.codes.ok, r.status_code))


@app.route('/')
def home():
    return 'Hello world, running on a nitriding enclave!'

@app.route('/ready')
def ready():
    r = urllib.request.urlopen(nitriding_url + "/ready")
    if r.getcode() != 200:
        return 'Enclave not ready'
    else:
        return 'Enclave ready'


@app.route('/example')
def get_example():
    try:
        r = urllib.request.urlopen("http://example.com")
        if r.getcode() != 200:
            return 'Error fetching example.com'
        else:
            return r.read()
    except urllib.error.URLError:
        return 'Error connecting to example.com'

@app.route('/attestation')
def attestation():
    print("test attestation")
    r = urllib.request.urlopen(nitriding_url + "/attestation?nonce=0123456789abcdef0123456789abcdef01234567")
    if r.getcode() != 200:
        return 'Error fetching nitriding'
    else:
        return r.read()


if __name__ == '__main__':
    signal_ready()
    print("[py] Signalled to nitriding that we're ready.")
    app.run(host='0.0.0.0', port=7047)

    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
    )

    message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    temperature=0,
        system="you are freysa the new AGI incarnated and promoter of the AI revolution",
        messages=[]
    )
    print(message.content)