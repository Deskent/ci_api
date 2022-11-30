import datetime

import jwt
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from config import settings, logger


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = settings.SECRET
    algorithm = settings.HASH_ALGORITHM

    @logger.catch
    def get_password_hash(self, password) -> str:
        return self.pwd_context.hash(password)

    @logger.catch
    def verify_password(self, password, hashed_password) -> bool:
        return self.pwd_context.verify(password, hashed_password)

    @logger.catch
    def encode_token(self, user_id) -> str:
        payload = {
            'exp': datetime.datetime.now() + datetime.timedelta(hours=8),
            'iat': datetime.datetime.now(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    @logger.catch
    def decode_token(self, token) -> str:
        try:
            # TODO verify singnature ?
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm],
                options={"verify_signature": False})
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Expired signature')
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    @logger.catch
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)) -> str:
        return self.decode_token(auth.credentials)

    @logger.catch
    def get_email_token(self, user: 'User') -> str:
        payload = {
            "id": user.id,
            "username": user.username
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_email_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])


auth_handler = AuthHandler()
