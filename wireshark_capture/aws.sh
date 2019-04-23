#!/bin/bash

# if you use your own certificates, emulating the CC3200 use this command:
# 
# openssl s_client -connect a7spspkufiddy-ats.iot.us-east-1.amazonaws.com:8443 -cert use/client.der -certform DER -key use/private.der -keyform DER -crlf


# otherwise this works for all intents and pruposes.
cat -n | openssl s_client -connect a7spspkufiddy-ats.iot.us-east-1.amazonaws.com:8443 -crlf
