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

# Requisições da api autenticação e autorização do usuário da aplicação
 
from fastapi import APIRouter, status, HTTPException, Depends, Response, Form
from typing import Annotated
from app.database import db_session
from app.models import Usuario
from fastapi.security import OAuth2PasswordRequestForm
from app.libs.security import create_access_token, create_refresh_token, verify_password, usuario_logado, check_access, get_hashed_password
import app.config as config
import datetime
 
router = APIRouter(prefix='/api/v1', tags=['login']) 

@router.post('/token', summary='Obter o token JWT para acesso a api')
def login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):  
    """
    Obtém o token JWT para acesso a api
    """
    session = db_session() 
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="E-mail ou senha inválidos.") 
    usuario = session.query(Usuario).filter(Usuario.email == form_data.username).first()   
    if not usuario:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail ou senha inválidos.")
    if not verify_password(form_data.password, usuario.senha):
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail ou senha inválidos.")
    jwt_payload = {
        "sub": usuario.id,
        "name": usuario.nome,
        "email": usuario.email,
        "roles": [r.codigo for r in usuario.perfis]
    }
    access_token = create_access_token(jwt_payload)
    refresh_token = create_refresh_token(jwt_payload)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    token = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
    } 
    return token

@router.post('/login/altera-senha/1', summary='Enviar e-mail solicitando alteração de senha', include_in_schema=False)
def trocar_senha(email: Annotated[str, Form()], response: Response):  
    """
    Enviar e-mail solicitando alteração de senha
    https://mailtrap.io/ DD@9B72@FB57233C
    https://github.com/railsware/mailtrap-python

    """
    session = db_session() 
    usuario = session.query(Usuario).filter(Usuario.email == email).first()   
    if not usuario:
        raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="E-mail ou senha inválidos.")
    
    jwt_payload = {
        "email": email
    }
    expira = datetime.timedelta(minutes=60) # Minutos    
    token = create_access_token(jwt_payload, expira) 
    url = f'{config.URL_BASE}/altera-senha/{token}'
    return url
 

@router.post('/login/altera-senha/2', summary='Alterar a senha por meio de email de recuperação', include_in_schema=False)
def nova_senha(token: Annotated[str, Form()], response: Response, senha: Annotated[str, Form()] = None):  
    """
    Altera a senha por meio de email de recuperação
    """
    session = db_session() 
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    usuario = usuario_logado(token)
    email = usuario['usuario_email']
    if senha is None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha inválida.")    
    usuario_db = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario_db:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail inválido.") 
    usuario_db.senha = get_hashed_password(senha) 
    session.commit()
    session.refresh(usuario_db)   
    return usuario_db  