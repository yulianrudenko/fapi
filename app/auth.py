from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

from .selectors import get_user

SECRET_KEY = '96wgqj7=^omp+av!-i+j6=lom6jl@av1ofh^zzwu347&otx_jb'
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    to_encode['exp'] = expires_at
    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception
    user_id: str = payload.get('user_id')
    if user_id is None:
        raise credentials_exception
    user = get_user(id=user_id)
    if user is None:
        raise credentials_exception
    return user
