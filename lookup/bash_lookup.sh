#!/bin/bash

# fill in the connect_command to establish connection to server, don't forget -showcerts option!
# a few examples are provided here for AWS IoT, maker.ifttt.com, and google.com


# amazon command, SHA-1
#connect_command="openssl s_client -connect a7spspkufiddy-ats.iot.us-east-1.amazonaws.com:8443 -crlf -showcerts -verify 5"

# ifttt command, SHA-1
connect_command="openssl s_client -connect maker.ifttt.com:443 -crlf -showcerts -verify 5"

#google command, SHA-1
#connect_command="openssl s_client -connect google.com:443 -crlf -showcerts -verify 5"

# base name of folder for outputs.
f_name="cert_chain"
f_num="0"
folder="$f_name"

# find a new directory name for certificate chain output
while [ -e $folder ]; do
    f_num="$(($f_num+1))"
    folder="$f_name$f_num"
done

# make new directory
mkdir $folder

# fetch certificate chain, uses command variable set above
echo "`$connect_command < /dev/null 2> /dev/null`" | awk '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/{ if(/BEGIN/){a++}; out="'$folder'/cert"a".crt"; print >out}'

# move into directory, supress output
pushd $folder > /dev/null 2> /dev/null

# status update
echo "Fetched certificate chain, saved to ./$folder"

# fetch information
first_file=`ls | grep cert | head -1`
last_file=`ls | grep cert | tail -1`
number=`ls | grep cert | wc -l`

# make sure at least one certificate was returned
if [ "$number" -lt "1" ]; then
    echo "Handshake error retreiving certificate chain" >&2
    exit 1
fi

# find intermediate certificates, all but first in chain
intermediates="`ls | grep cert | tail -$(($number-1))`"

# computer the issuer's hash of last certificate for quick lookup
hash=`openssl x509 -in $last_file -noout -issuer_hash`

# status update
echo "Looking for valid root certificate: $hash"

# lookup issuer hash, store in hash format, allows quick lookup
# only works on unix systems, but this is a bash script :/
name=`ls /etc/ssl/certs/ | grep "$hash"`

# if lookup successful, take first match
if [ "$?" -eq "0" ]; then
    
    # count matches
    count=`echo $name | wc -l`

    # take first and follow symlink to actual certificate
    # then extract file name
    name=`echo "$name" | head -1`
    name_path=`readlink -f "/etc/ssl/certs/$name"`
    name=`basename $name_path`
    
    # status update and copy file 
    echo "Found $count root certificates, taking first: $name"
    echo "Copying to ./$folder/$name"
    cp "$name_path" "."
else
    echo "Could not find matching root certificate."
fi

# verfiy root certificate

#openssl verify -show_chain -untrusted cert2.crt -untrusted cert3.crt -untrusted cert4.crt cert1.crt 

# build verification command from intermediate, root, and server certificates.
ver_com="openssl verify -show_chain"

for file in $intermediates; do
    ver_com="$ver_com -untrusted $file"
done

ver_com="$ver_com -trusted $name $first_file"

echo ""
echo ""
echo "Verifying root certificate and chain, command:"
echo "$ver_com"
echo ""
output="`$ver_com`"
result=$?

echo "$output"

if [ "$result" -eq "0" ]; then
    echo ""
    echo ""
    echo "Root certification lookup sucessful!"
    echo "Here is information about the chain:"
    echo ""
    flat=`echo $intermediates`
    files="$first_file $flat $name"

    for file in `echo $files`; do
        type=`openssl x509 -in $file -text -noout | grep "Signature Algorithm" | tail -1 | awk '{ print $3 }'`
        subject=`openssl x509 -in $file -noout -subject`
        echo "$file: $type"
        #echo "$subject"
        #echo ""
    done
fi

# return to original working directory
popd > /dev/null 2> /dev/null
