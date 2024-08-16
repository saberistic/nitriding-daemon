#!/bin/sh

nitriding -fqdn eternis.saberistic.com -appwebsrv http://127.0.0.1:80 -ext-pub-port 443 -intport 8080 &
echo "[sh] Started nitriding."

sleep 1

mount /tmp -o remount,exec
ls
cd /usr/local/bin/ 
/usr/local/bin/notary-server --config-file /app/config/config.yml
echo "[sh] Notary server closed."
