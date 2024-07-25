#!/bin/sh

nitriding -fqdn eternis.saberistic.com -appwebsrv http://127.0.0.1:80 -ext-pub-port 443 -intport 8080 &
echo "[sh] Started nitriding."

sleep 1

tlsproxy --config=/bin/config.yaml --passphrase=1234
echo "[sh] Ran tlsproxy script."
