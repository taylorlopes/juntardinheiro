"""
Copyright (c) All Rights Reserved 

THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND EXPRESS
OR IMPLIED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED 
IN THIS NOTICE BE LIABLE FOR ANY CLAIM OR CONSEQUENTIAL DAMAGES OR ANY 
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE DATA OR PROFITS, WHETHER
IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

Author Taylor Lopes <taylorlopes@gmail.com>
""" 

# Segurança, OAuth, JWT

from fastapi import  status, HTTPException, Request
from jose import JWTError, jwt
import bcrypt
import os
import json
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
import app.config as config
import pytz 
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/token",
    scheme_name="admin_oauth2_schema",
    auto_error=False
) 

def get_hashed_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password.encode('utf-8'))

def create_access_token(jwt_payload: dict, expires_delta: int = None) -> str:
    dt_now = datetime.now(pytz.timezone(config.APP_TIME_ZONE))
    if expires_delta is not None:
        expires_delta = dt_now + expires_delta
    else:
        expires_delta = dt_now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_payload.update({"iat": dt_now})
    jwt_payload.update({"exp": expires_delta})
    to_encode = jwt_payload
    encoded_jwt = jwt.encode(to_encode, os.environ.get('JWT_SECRET_KEY'), config.ALGORITHM)
    return encoded_jwt

def create_refresh_token(jwt_payload: dict, expires_delta: int = None) -> str:
    dt_now = datetime.now(pytz.timezone(config.APP_TIME_ZONE))
    if expires_delta is not None:
        expires_delta = dt_now + expires_delta
    else:
        expires_delta = dt_now + timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)
    jwt_payload.update({"iat": dt_now})
    jwt_payload.update({"exp": expires_delta})
    to_encode = jwt_payload
    encoded_jwt = jwt.encode(to_encode, os.environ.get('JWT_REFRESH_SECRET_KEY'), config.ALGORITHM)
    return encoded_jwt
 

def check_access(token: str, roles = []):
    if not token:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Token não encontrado",
      )
    try:
        payload = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=[config.ALGORITHM])
    except JWTError:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Token inválido"
      ) 


    if 'roles' in payload:

        if payload['roles'] == []:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operação não autorizada"
        ) 
                
        for role in payload['roles']:
            if role not in roles:
                raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Operação não autorizada"
            )
 
def usuario_logado(token: str):
    if not token:
        return {
            'usuario_logado' : False 
        }
    try:        
        payload = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=[config.ALGORITHM])
    except JWTError:
        return {
            'usuario_logado' : False 
        }
    return {
        'usuario_logado' : True,
        'usuario_id' : payload['sub'] if 'sub' in payload else None,
        'usuario_nome' : payload['name'] if 'name' in payload else None,
        'usuario_email' : payload['email'] if 'email' in payload else None,
        'usuario_perfis' : payload['roles']  if 'roles' in payload else None
    } 
