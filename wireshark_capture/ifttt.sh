#!/bin/bash

cat -n | openssl s_client -connect maker.ifttt.com:443 -crlf
