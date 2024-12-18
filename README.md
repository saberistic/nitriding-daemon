# TEE Agent with Nitriding 

## Concept

- this is a server running in a nitro enclave instance
- we use nitriding to generate aws attestation of the code 

## Environment variables

The env variable system is similar to variables in a smart contract. 
An operator address is hardcoded before enclave initialization.
After deployment, the operator can set the environment variables using a SECP256k1 signature.
Message is (tee_name, function, var_name, new_value).
Variables can also have immutable property, and therefore be set only once.
The difference with a smart contract is that the environment variables can be set to hidden.
Hidden variables can be changed to public, but not the other way.
Similarly, mutable variables can be changed to immutable, but not the other way.

## Run

- Create nitro ec2 instance 
- clone repo 
- go to the app folder you want to launch
- run make 
- run ./gvproxy.sh
- make sure you exposed the app port in AWS security group

## Dev

edit /api/service.py to add new endpoints

TODO:
- https 
- openrouter api endpoint
- create state for multiple operator, using a sort of address mapping
- create a role access system for each operator, for each method
- add agent public key to aws attestation
- instructions for verification of code attestation
- separate business logic from enclave endpoint
- add toolings
- save state in IPFS


 [Nitriding doc](https://github.com/brave/nitriding-daemon)