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

# Requisições da api de usuário

from fastapi import APIRouter, status, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from typing import List, Optional, Annotated
from app.database import db_session
from app.libs.utils import populate
from app.libs.security import oauth2_scheme, check_access, usuario_logado, get_hashed_password
import uuid
from app import models, schemas
from sqlalchemy import select
import json
import requests
import app.config as config

router = APIRouter(prefix='/api/v1', tags=['usuarios']) 

@router.post('/usuarios', response_model=schemas.Usuario, summary='Criar um registro de usuário') # pragma: no cover
def cadastrar_usuario(usuario: schemas.UsuarioInput):
    """
    Cria um registro de usuário
    """ 
    session = db_session()
    if (session.execute(select(models.Usuario).where(models.Usuario.email == usuario.email))).first():
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail de usuário já cadastrado.") 
    usuario_db = models.Usuario(**usuario.model_dump()) 
    usuario_db.id = str(uuid.uuid4())
    usuario_db.senha = get_hashed_password(usuario.senha)  
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db) 
    perfil_sistema_id = 2 # USER_APP
    session.execute(models.usuario_perfil_sistema.insert().values(usuario_id=usuario_db.id, perfil_sistema_id=perfil_sistema_id)) 
    session.commit()
    usuario = session.get(models.Usuario, usuario_db.id)
    return usuario_db

@router.get('/usuarios', response_model=List[schemas.Usuario], summary='Obter todos registros de usuário', description='**Perfil:** USER_ADMIN')
def obter_usuarios(token: Annotated[str, Depends(oauth2_scheme)]): 
    """
    Obtém todos registros de usuário
    """
    # check_access(token, ['USER_ADMIN'])
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    session = db_session()
    usuarios = session.query(models.Usuario).all()
    return usuarios

@router.get('/usuarios/{usuario_id}', response_model=schemas.Usuario, summary='Obter um registro de usuário')
def obter_usuario(token: Annotated[str, Depends(oauth2_scheme)], usuario_id: str): 
    """
    Obtém um registro de usuário
    """    
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    session = db_session()        
    usuario = session.get(models.Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Nenhum usuário encontrado.")
    return usuario

@router.put('/usuarios/{usuario_id}', response_model=schemas.Usuario, summary='Atualizar um registro de usuário')
def atualizar_usuario(token: Annotated[str, Depends(oauth2_scheme)], usuario_id: str, usuario: schemas.UsuarioInput): # pragma: no cover
    """
    Atualizar um registro de usuário'
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    session = db_session()
    usuario_db = session.get(models.Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail=f"Registro de usuário não encontrado.")    
    fields = usuario.model_dump(exclude_unset=True)
    for key, value in fields.items():
        setattr(usuario_db, key, value)
    if usuario.senha is not None:
        usuario_db.senha = get_hashed_password(usuario.senha) 
    if usuario.email is not None and (session.execute(select(models.Usuario).where(models.Usuario.email == usuario.email))).first():
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail de usuário já cadastrado.")
    session.commit()
    session.refresh(usuario_db)   
    return usuario_db 

# @router.delete('/usuarios/{usuario_id}', response_model=schemas.Usuario, summary='Exclui um registro de usuário')
@router.delete('/usuarios/{usuario_id}', summary='Excluir um registro de usuário')
def excluir_usuario(token: Annotated[str, Depends(oauth2_scheme)], usuario_id: str):  # pragma: no cover
    """
    Exclui um registro de usuário
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])

    # Somente permite se for do próprio usuário logado
    usuario = usuario_logado(token)    
    if 'usuario_id' not in usuario or usuario_id != usuario['usuario_id']:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operação não permitida.")   

    r = requests.get(url=f"{config.URL_BASE}/api/v1/carteiras/usuarios/{usuario_id}",                      
                     headers={"Authorization": f"Bearer {token}"},
                     verify=False) 
    carteiras = json.loads(r.text)  
    for carteira in carteiras:
        r = requests.delete(url=f"{config.URL_BASE}/api/v1/carteiras/{carteira['id']}",                      
                        headers={"Authorization": f"Bearer {token}"},
                        verify=False)          
    session = db_session()
    usuario = session.get(models.Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Registro de usuário não encontrado.")
    session.delete(usuario)
    session.commit() 
    return usuario
 