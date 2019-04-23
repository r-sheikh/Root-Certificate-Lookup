# Code adapted from multiple sources:
# https://gist.github.com/brandond/f3d28734a40c49833176207b17a44786
# https://gist.github.com/uilianries/0459f59287bd63e49b1b8ef03b30d421
# https://www.programcreek.com/python/example/96059/OpenSSL.crypto.X509Store
# https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_default_certs

# Other references used:
# https://pyopenssl.org/en/stable/api/crypto.html#x509-objects
# https://pyopenssl.org/en/stable/api/ssl.html
# https://pyopenssl.org/en/stable/api/ssl.html?highlight=get_peer_cert_chain
# https://pyopenssl.org/en/stable/api/crypto.html

import sys
import socket

# make sure use has the pyOpenSSL module installed
try:
    from OpenSSL import SSL, crypto
except:
    print("\nERROR:\n    python module pyOpenSSL needs to be installed. Install with:\n    pip install pyopenssl\n")
    exit()

import ssl


# used if default ssl path settings fail to find certificates under unix os's
# whether this is needed depends on how OpenSSL is compiled :/
backup_default_unix_ca_file='/etc/ssl/certs/ca-certificates.crt'


# https://gist.github.com/uilianries/0459f59287bd63e49b1b8ef03b30d421
# https://www.programcreek.com/python/example/96059/OpenSSL.crypto.X509Store
# https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_default_certs
def find_issuer(certificate):

    # find certificate store unique to OS    
    context = ssl.create_default_context()
    context.load_default_certs()
    cert_list = context.get_ca_certs(binary_form=True)

    if(len(cert_list) < 1):
        context.load_verify_locations(cafile=backup_default_unix_ca_file)
        cert_list = context.get_ca_certs(binary_form=True)
        if(len(cert_list) < 1):
            print('Fatal error: unable to locate ca-certificates.')
            exit(1)

    found = []      
    
    for der_cert in cert_list:

        # emulates CC3200 in which there is only one root in store 
        # ASN1 === DER
        store = crypto.X509Store()
        ld_crt = crypto.load_certificate(crypto.FILETYPE_ASN1, der_cert)
        store.add_cert(ld_crt)
        store_ctx = crypto.X509StoreContext(store, certificate)

        # raises exception on verification failure
        try:
            store_ctx.verify_certificate()
            tup = (ld_crt,der_cert)
            found.append(tup)
        except:
            continue 

    return found


# https://gist.github.com/brandond/f3d28734a40c49833176207b17a44786
def get_chain(hostname):
    print('\n\nGetting certificate chain for {0}'.format(hostname))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = SSL.Connection(context=SSL.Context(method=SSL.TLSv1_2_METHOD), socket=sock)
    sock.settimeout(5)
    sock.connect((hostname, 443))
    sock.setblocking(1)
    sock.do_handshake()

    chain = sock.get_peer_cert_chain()
    for (idx, cert) in enumerate(chain):
        print(' {0} s:{1}'.format(idx, cert.get_subject()))
        print(' {0} i:{1}'.format(' ', cert.get_issuer()))
    sock.shutdown()
    sock.close()

    return chain


length = len(sys.argv)
filename = ''

if (length > 1):
    hostname = str(sys.argv[1])
    if(length > 2):
        filename = str(sys.argv[2])
else:
    print('Usage: python3 {0} <host name> [<filename>]\n'.format(str(sys.argv[0])))
    print('Provide file names without extensions.')
    print('Roots will be enumerated starting from zero with a .der extension.')
    print('Default filename is ''root_cert''.')
    print('Example output name: ''root_cert0.der''')
    exit(1)

if hostname:

    hostname = hostname.strip('.').strip()
    chain = None

    # attempt to fetch seerver certificate chain
    try:
        hostname.index('.')
        chain = get_chain(hostname)
    except Exception as e:
        print('   f:{0}'.format(e))
        exit()

    # find root certificate(s)
    if(chain and len(chain) > 0):    
        found = find_issuer(chain[-1])
    else:
        found = []

    # check if a root certificate was found on file
    if(len(found) > 0):
        
        print("\n\nFound valid roots on file:\n")
        
        # generate default output filename if needed
        if not(filename):
            filename = 'root_cert'

        # iterate over found roots
        for idx,cert in enumerate(found):
            
            fname = '{0}{1}.der'.format(filename,idx)

            # print root cert info
            print('Writing root #{0} to file {1}'.format(idx,fname))
            print('  s:{0}'.format(cert[0].get_subject()))
            print('  i:{0}'.format(cert[0].get_issuer()))
            print()    

            # write certificate to file, DER format
            f = open(fname, 'wb')
            f.write(cert[1])
            f.close()

    else:
        print('No appropraite root certificates found on file.')
        exit(1)
