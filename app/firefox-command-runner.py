#!/usr/bin/env python2

import sys
import os
import json
import struct
import subprocess
import tempfile

# Read a message from stdin and decode it.
def getMessage():
    rawLength = sys.stdin.read(4)
    if len(rawLength) == 0:
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    return sys.stdin.read(messageLength).decode('string_escape').strip("'\"")


# Encode a message for transmission,
# given its content.
def encodeMessage(messageContent):
    encodedContent = json.dumps(messageContent)
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}


# Send an encoded message to stdout
def sendMessage(encodedMessage):
    sys.stdout.write(encodedMessage['length'])
    sys.stdout.write(encodedMessage['content'])
    sys.stdout.flush()

# thanks @Lennon Hill for the cookie management code (see https://github.com/lennonhill/cookies-txt)
cookie_header = \
    '# Netscape HTTP Cookie File\n' + \
    '# https://curl.haxx.se/rfc/cookie_spec.html\n' + \
    '# This is a generated file! Do not edit.\n\n';

def makeCookieJar(cookies):
    subprocess.check_output(['/tmp/echo_me', "making cookie jar"])
    with tempfile.NamedTemporaryFile(mode='w+t', suffix=".txt", delete=False) as my_jar:
        my_jar.write(cookie_header)
        my_jar.write(''.join(cookies))
        return my_jar.name

while True:
    try:
        my_jar = None
        #receivedMessage = json.loads(getMessage())
        receivedMessage = {'url':"--help", 'cookies':['bla']}
        url = receivedMessage['url']
        use_cookies = bool('cookies' in receivedMessage and receivedMessage['cookies'])

        # sendMessage(encodeMessage('Starting Download: ' + url))
        try:
            command_vec = ['youtube-dl']
            config_path = os.path.join(os.pardir, 'config')
            if os.path.isfile(config_path):
                command_vec += ['--config-location', config_path]

            if use_cookies:
                my_jar = makeCookieJar(receivedMessage['cookies'])
                subprocess.check_output(command_vec + ['--cookies', my_jar, url])
            else:
                subprocess.check_output(command_vec + [url])

            sendMessage(encodeMessage(f'Finished Downloading to /data/down: {url}'))
        except Exception as err:
            sendMessage(encodeMessage(f'Some Error Downloading: {url}: {str(err)}'))
        finally:
            # be sure to remove the cookie storage even in case of exception
            if use_cookies and my_jar:
                os.unlink(my_jar)
    except Exception as err:
        sendMessage(encodeMessage(f'JSON error: {str(err)}'))

