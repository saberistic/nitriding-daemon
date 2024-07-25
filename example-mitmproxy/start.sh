#!/bin/sh

nitriding -fqdn eternis.saberistic.com -appwebsrv http://127.0.0.1:80 -ext-pub-port 443 -intport 8080 &
echo "[sh] Started nitriding."

sleep 1

mount /tmp -o remount,exec
cd /root
cp /bin/addon.py .
mitmdump --listen-port 10080 --flow-detail 3 --scripts addon.py
echo "[sh] Ran mitmdump script."
