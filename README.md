# Root-Certificate-Lookup

This repo provides bash and python scripts that use OpenSSL libraries/modules to fetch the root certificates that would be used to verify a certificate chain presented by a given server during a TLS handshake. It is targeted for use in IoT applications where it is often difficult to find the appropriate certificates to use, especially if the library implementing the TLS protocol takes a minimalistic aproach to certificate chain verification.

#### Folder Contents:
* __example_outputs:__ contains folders that demonstrate the scripts' outputs for both the python and bash script with a couple of different servers.
* __lookup_scripts:__ contains the bash and python scripts that can be used for root certificate lookup.
  * bash_lookup.sh : A bash script that will fetch the entire certificate chain, lookup the root certificate that verifies the last certificate in the chain and store all of this in an output folder. Will also print information about the chain as it parses the inputs. The script will need to be updated with the correct host and port information for your application. Some comment in-script that show how to establish connections to AWS's IoT servers, maker.ifttt.com, and google.com.
  * python_lookup.py : A python3 script that *should* work on any unix or windows based operating system. Might have to install the pyopenssl pip3 library. Tested working on Windows 10 and Ubuntu distributions. Outputs some information about the server certificate chain and saves the root certificate to file. Would recomend this script even though the output is less verbose as it is mostly independent of the underlying OS. The basic command-line syntax is shown below.
  ``` python3 python_lookup.py <host name> [<output filename>]```
* __wireshark_capture:__ Provided for the curious and those that land here after reading my paper. This folder contains the wireshark packet captures for the TLS handshakes establishing connections to maker.ifttt.com and AWS's IoT servers. The folder also provides two bash scripts that use OpenSSL's s_client module to establish the connections for packet capture. 
#### Sources
A lot of this work was influenced by other developers on the internet here is a list of the resources whose work helped contributed to the development of this project:
* https://unix.stackexchange.com/questions/368123/how-to-extract-the-root-ca-and-subordinate-ca-from-a-certificate-chain-in-linux
* https://gist.github.com/brandond/f3d28734a40c49833176207b17a44786
* https://gist.github.com/uilianries/0459f59287bd63e49b1b8ef03b30d421
* https://www.programcreek.com/python/example/96059/OpenSSL.crypto.X509Store

#### References:
* Python references:
  * https://pyopenssl.org/en/stable/api/crypto.html
  * https://pyopenssl.org/en/stable/api/crypto.html#x509-objects
  * https://pyopenssl.org/en/stable/api/ssl.html
  * https://pyopenssl.org/en/stable/api/ssl.html?highlight=get_peer_cert_chain
  * https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_default_certs


* OpenSSL references:
  * https://www.openssl.org/docs/man1.0.2/man1/s_client.html
  * https://www.openssl.org/docs/man1.0.2/man1/openssl-verify.html
