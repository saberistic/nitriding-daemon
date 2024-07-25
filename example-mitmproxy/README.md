Nitriding example
=================

This directory contains an example application; a lightweight
[Python script](addon.py)
that modifies request and response.  The project's
[Dockerfile](Dockerfile) adds the nitriding standalone executable along with the
enclave application, consisting of the
[Python script](addon.py)
and a
[shell script](start.sh)
that invokes nitriding in the background, followed by running the mitmproxy and addon script.

To build the nitriding executable, the Docker image, the enclave image, and
finally run the enclave image, simply run:

    make
