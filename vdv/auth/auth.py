from jose import jwt
from vdv.auth.config import CONFIG, PROVIDER

JWT_SIGN_ALGORITHM = 'RS256'
JWT_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2306g4lK+eGXGCHABrCp
Qh/kds9Aky13xeGCzgILUesyi5yvxiqi8AVuVvxQ3cM5JZZRxbIPOYqjISSQi5qm
xqxtkd2nVmgewHYbLUEkEpt4x57mfvEitST2PvLjjF1aAnwtM/QUw4vgjNtBjS4y
yAGKvHGx8UXxKv9O1RlaA7JLOx0qYEpbnx1f8R7f8q3kIS18xem7COOnpvfol9sd
oGSaqxg+Dtcqw+w23fYkn/BrkH0fvuIW0r8ypMTopTfE+0rQcAEJ8Zs+86aNYHnp
CHnH3akf3XIHEwdEcPs+tv2O4Iz0aS7NK9NfnVpe2RP1ePnJPo9R0DhLuQynrqKc
PQIDAQAB
-----END PUBLIC KEY-----'''

def Configure(**kwargs):
    CONFIG.update(kwargs)

def Validate(token, provider):
    try:
        aud = jwt.get_unverified_claims(token).get('aud')  # we accept whatever audience encoded in the token
        res = jwt.decode(token, JWT_PUBLIC_KEY, issuer=CONFIG[provider]['access_token_url'], audience=aud,
                         algorithms=JWT_SIGN_ALGORITHM)
        return None, res

    except jwt.JWTError as e:
        return str(e), None
