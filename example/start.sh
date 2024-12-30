#!/bin/sh

nitriding -fqdn example.com -ext-pub-port 443 -intport 8080 -wait-for-app &
echo "[sh] Started nitriding."

sleep 1


cd bin

pip3 install flask anthropic ecdsa openai json

python3 service.py

echo "[sh] Ran Python script."
