sudo pkill -f gvproxy

sudo rm -rf /tmp/network.sock

sudo gvproxy -listen vsock://:1024 -listen unix:///tmp/network.sock &

sleep 2

#open port for server
sudo curl --unix-socket /tmp/network.sock \
    http:/unix/services/forwarder/expose \
    -X POST \
    -d '{"local":":7047","remote":"192.168.127.2:7047"}'

# nitriding ports
sudo curl --unix-socket /tmp/network.sock \
    http:/unix/services/forwarder/expose \
    -X POST \
    -d '{"local":":443","remote":"192.168.127.2:443"}'
