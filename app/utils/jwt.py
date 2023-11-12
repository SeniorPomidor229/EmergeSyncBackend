import jwt

def encode_token(payload:dict) -> str:
    token = jwt.encode(
        payload=payload,
        key="SECRET"
    )
    return token

def decode_token(token:str) -> dict:
    payload = jwt.decode(
        jwt=token,
        key="SECRET",
        algorithms="HS256"
    )
    return payload