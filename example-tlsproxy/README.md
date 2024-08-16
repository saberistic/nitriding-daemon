Nitriding example
=================

This directory contains an example application; a tlsproxy.  The project's
[Dockerfile](Dockerfile) adds the nitriding standalone executable along with the
enclave application, consisting of a
[binary](tlsproxy)
and a
[config](config.yaml)
and a
[shell script](start.sh)
that invokes nitriding in the background, followed by running the Python script.

To build the nitriding executable, the Docker image, the enclave image, and
finally run the enclave image, simply run:

    make
