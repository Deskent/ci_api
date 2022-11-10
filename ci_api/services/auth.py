import datetime

from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = 'secret'

    def get_password_hash(self, password) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password, hashed_password) -> bool:
        return self.pwd_context.verify(password, hashed_password)

    def encode_token(self, user_id) -> str:
        payload = {
            'exp': datetime.datetime.now() + datetime.timedelta(hours=8),
            'iat': datetime.datetime.now(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token) -> str:
        try:
            # TODO verify singnature ?
            payload = jwt.decode(
                token, self.secret, algorithms=['HS256'], options={"verify_signature": False})
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Expired signature')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)) -> str:
        return self.decode_token(auth.credentials)
