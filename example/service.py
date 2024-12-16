from flask import Flask, request
import time
import urllib.request
import anthropic
import ssl


app = Flask(__name__)

nitriding_url = "http://127.0.0.1:8080/enclave"

nitriding_ext_url = "https://18.207.122.203"


def signal_ready():
    r = urllib.request.urlopen(nitriding_url + "/ready")
    if r.getcode() != 200:
        raise Exception(
            "Expected status code %d but got %d"
            % (requests.status_codes.codes.ok, r.status_code)
        )


@app.route("/")
def home():
    return f"""Hello world, running on a nitriding enclave! <br/>
        List of endpoints: <br/>
        /attestation <br/>
        /callmodel <br/>"""


@app.route("/attestation")
def attestation():
    print("test attestation")

    url = (
        nitriding_ext_url
        + "/enclave/attestation?nonce=0123456789abcdef0123456789abcdef01234567"
    )
    print(url)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    r = urllib.request.urlopen(url, context=context)
    if r.getcode() != 200:
        return "Error fetching nitriding"
    else:
        return r.read()


@app.route("/callmodel")
def callmodel():
    # Get the message from URL parameter, default to "hello" if not provided
    user_message = request.args.get("message", "hello")

    client = anthropic.Anthropic(
        api_key="",
    )

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0,
        system="you are freysa the new AGI incarnated and promoter of the AI revolution",
        messages=[
            {"role": "user", "content": [{"type": "text", "text": user_message}]}
        ],
    )
    print(message.content[0].text)
    return message.content[0].text


if __name__ == "__main__":
    signal_ready()
    print("[py] Signalled to nitriding that we're ready.")
    app.run(host="0.0.0.0", port=7046)
