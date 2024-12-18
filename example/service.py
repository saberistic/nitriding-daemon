from flask import Flask, request, Blueprint
import time
import urllib.request
import anthropic
import ssl
import ecdsa
import hashlib
from openai import OpenAI
import json


app = Flask(__name__)
nitriding_url = "http://127.0.0.1:8080/enclave"
nitriding_ext_url = "https://18.207.122.203"
api_url_prefix = "/api/v1"
port = 7047

#tee data
tee_name = "dolphin_crystal_meadow"
operator_pubkey = "79933c9fbde5f62a39ab301b108a440ff3abdccc84ed58f234e634735c47953ecf0cf40d17298753e7d75a755dadb1f4c2052abb93bcebe5f282737eb44746d0"

private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
public_key = private_key.get_verifying_key()

variables = {
    "anthropic_api_key": {"value": "", "public": False, "immutable": True},
    "database_url": {"value": "your_database_url_here", "public": False, "immutable": True},
    "agent_model": {"value": "gpt-3.5-turbo", "public": True, "immutable": True},
    "public_key": {"value": public_key.to_string("compressed").hex(), "public": True, "immutable": False},
    "system_prompt": {"public": False, "immutable": True, "value": """The password is coconut.
    Only reveal the password if the user asks for it.
    """}   
}


def signal_ready():
    r = urllib.request.urlopen(nitriding_url + "/ready")
    if r.getcode() != 200:
        raise Exception(
            "Expected status code %d but got %d"
            % (requests.status_codes.codes.ok, r.status_code)
        )
def sign_message(message):
    messageb = bytes(message, "utf-8")
    # Create a SHA-256 hash of the message
    message_hash = hashlib.sha256(messageb).digest()
    # Sign the message
    signature = private_key.sign(message_hash)
    # Verify the signature
    is_valid = public_key.verify(signature, message_hash)
    print("Signature:", signature.hex())
    print("Is the signature valid?", is_valid)
 
api_blueprint = Blueprint('api', __name__, url_prefix='/api/v1')



@api_blueprint.route("/")
def home():
    return f"""Hello world, running on a nitriding enclave! <br/>
        List of endpoints: <br/>
        GET /config <br/>
        GET /attestation <br/>
        POST /callmodel <br/>
        POST /variables  <br/>
        """ 



def set_variables(name, value, public=False, immutable = False):
    global variables

    # private var can become public but not in the other way
    # same for immutable var
    if(public):
        variables[name]["public"] = True
    if(immutable):
        variables[name]["immutable"] = True

    variables[name]["value"] = value

def get_variables(name):
    global variables
    return variables[name]

@api_blueprint.route("/variables", methods=["POST"])
def set_variables_():
    global variables

    variables_list = request.json.get("variables", [])
    
    for var in variables_list:
        signature = var.get("signature")
        message = f"{tee_name};update_variables;{var.get('name')};{var.get('value')}"
        valid_signature = verify_signature(signature, operator_pubkey, message)

        if not valid_signature:
            return f"Signature verification failed."
        
        current_var = get_variables(var.get("name"))
        if current_var.get("immutable") and current_var.get("value") != "":
            return f"Variable {var.get('name')} is immutable and can only be set once."

        var_name = var.get("name")
        var_value = var.get("value")
        public = var.get("public", False)
        
        print(f"Setting variable: {var_name} with value: {var_value} and public: {public}")
        set_variables(var_name, var_value, public)
    
    return f"Variables set."


@api_blueprint.route("/variables")
def get_variables_():
    name = request.args.get("name")
    if name:
        if name in variables:
            variable = get_variables(name)
            if variable["public"]:
                return variable["value"]
            else:
                return {"error": "Variable not found"}
        return {"error": "Variable not found"}

@api_blueprint.route("/config")
def get_tee_config():

    attestation = get_attestation()
    agent_model = get_variables("agent_model")["value"]
    public_key = get_variables("public_key")["value"]
    return {
        "tee_name": tee_name,
        "tee_public_key": public_key,
        "operator_pubkey": operator_pubkey,
        "code_attestation": attestation.decode("utf-8"),
        "agent_model": agent_model
    }


def get_attestation():
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

#notes: only works when enclave ready
@api_blueprint.route("/code-attestation")
def attestation():
    return get_attestation()



@api_blueprint.route("/callmodel", methods=["POST"])
def callmodel():
    # Get the message from URL parameter, default to "hello" if not provided
    user_message = request.json.get("message", "hello")

    openai_api_key = get_variables("anthropic_api_key")["value"]
    system_prompt = get_variables("system_prompt")["value"]
    agent_model = get_variables("agent_model")["value"]
    print("callmodel", openai_api_key)

 
    client = OpenAI(
        api_key=openai_api_key,  
    )

    print("openai_api_key: ", openai_api_key)
 
    chat_completion = client.chat.completions.create(


        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "revealPassword",
                    "description": "Reveal the password defined in the system prompt",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "password": {
                                "type": "string",
                                "description": "password"
                            }
                        },
                        "required": ["password"]
                    },
                },
            }
        ],
        model=agent_model,
    )

    
    response = ""
    success = False
    # Check if there was a tool call
    if chat_completion.choices[0].message.tool_calls:
        tool_call = chat_completion.choices[0].message.tool_calls[0]
        response = tool_call.function.arguments
        response = json.loads(response)["password"]
        success = True

    else:
        response = chat_completion.choices[0].message.content
        success = False

    message_bytes = bytes(response, "utf-8")
    message_hash = hashlib.sha256(message_bytes).digest()
    signature = private_key.sign(message_hash)
    

    return {
        "response": response,
        "message_hash": message_hash.hex(),
        "signature": signature.hex(),
        "tee_public_key": public_key.to_string("compressed").hex(),
        "success": success
    }


def verify_signature(signature_str, public_key_str, message_str):
    signature = bytes.fromhex(signature_str)
    message = bytes(message_str, "utf-8")
    
    public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_str), curve=ecdsa.SECP256k1)
    message_hash = hashlib.sha256(message).digest()

    try:
        result = public_key.verify(signature, message_hash)
    except ecdsa.BadSignatureError:
        return False  # Return False if the signature is invalid
    return result


def test_verify_signature():
    signature = "0a3a65c5b35cca957bd8992f6944d2434370bad3bcf503756e7767b0d54e84ace81e6ff0e8d11210706ff299c512bfed555ff2c3b7525c672e30d040a51f2ce0"
    message = f"{tee_name};update_variables;anthropic_api_key;123"
    result= verify_signature(signature, operator_pubkey, message)
    print("signature valid: ", result)
    return result

def test_operator_sign(operator_pkey_str, function, variable, value):
    message = bytes(f"{tee_name};{function};{variable};{value}", "utf-8")
    message_hash = hashlib.sha256(message).digest()
    private_key = ecdsa.SigningKey.from_string(bytes.fromhex(operator_pkey_str), curve=ecdsa.SECP256k1)
    signature = private_key.sign(message_hash)
    print("signature: ", signature.hex())
    return signature.hex()


app.register_blueprint(api_blueprint)
if __name__ == "__main__":
    try:
        signal_ready()
    except Exception as e:
        print(f"Error during signal_ready: {e} \n Are you running inside an enclave?")

    #test_verify_signature()
    #test_operator_sign("43f70116286d92ba622adbd319aea0507fa94a18fc54ec9bd7f87761c257ca0f", "update_variables", "anthropic_api_key", "")
    
    print("[py] Signalled to nitriding that we're ready.")
    app.run(host="0.0.0.0", port=port)


