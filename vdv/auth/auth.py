from vdv.auth.config import CONFIG, PROVIDER

import urllib.request
import json

def Configure(**kwargs):
    CONFIG.update(kwargs)

def Validate(token, provider):
    try:
        response = urllib.request.urlopen(CONFIG[provider]['check_token_url'] + token)
        certs = response.read()
        return None, json.loads(certs)['access_type']
    except Exception as e:
        return str(e), None
