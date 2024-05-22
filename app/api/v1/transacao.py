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

# Requisições da api transações (aportes) do ativo de um usuário

from fastapi import APIRouter, Request, status, HTTPException, Depends
from app.database import db_session
from app import models, schemas
from typing import List, Optional, Annotated 
from sqlalchemy import select, delete, update 
from app.libs.security import oauth2_scheme, check_access, usuario_logado
import uuid
import json
import requests
import app.config as config

router = APIRouter(prefix='/api/v1', tags=['transacoes'])

@router.post('/transacoes', summary='Criar um registro de transação de ativo', include_in_schema=False) 
def cadastrar_transacao(token: Annotated[str, Depends(oauth2_scheme)], transacao: schemas.Transacao):  # pragma: no cover
    """
    Cadastra a transação de um ativo
    """        
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    transacao.id = str(uuid.uuid4()) 
    del transacao.tipo_transacao
    transacao_db = models.Transacao(**transacao.model_dump()) 
    session = db_session()
    session.add(transacao_db)
    session.commit()  
    return transacao_db 


@router.get('/transacoes/usuarios/{usuario_id}',  summary='Obter registros de transações de um usuário')
def obter_transacoes_usuario(token: Annotated[str, Depends(oauth2_scheme)], usuario_id: str):
    """
    Obtém as transações de um usuario
    """
    usuario = usuario_logado(token)
    check_access(token, ['USER_ADMIN', 'USER_APP'])  
    r = requests.get(url=f"{config.URL_BASE}/api/v1/carteiras/usuarios/{usuario['usuario_id']}",                      
                     headers={"Authorization": f"Bearer {token}"},
                     verify=False) 
    carteiras = json.loads(r.text)
    transacoes = []
    for carteira in carteiras:
        for classe_ativo in carteira['classes_ativos']: 
            for ativo in classe_ativo['ativos']: 
                for transacao in ativo['transacoes']:
                    transacoes.append({
                        "usuario_id": carteira['usuario_id'],
                        "carteira_id": carteira['id'],
                        "carteira_nome": carteira['nome'],
                        "classe_ativo_id": classe_ativo['id'],
                        "classe_ativo_nome": classe_ativo['nome'],
                        "grupo_ativo_nome": classe_ativo['grupo_ativo']['nome'],
                        "ativo_id": ativo['id'],
                        "ativo_ticker": ativo['ticker'],
                        "ativo_nome": ativo['nome'],
                        "tipo_ativo": ativo['tipo_ativo']['nome'],
                        "setor_nome": ativo['setor']['nome'],
                        "moeda_simbolo": ativo['moeda']['simbolo'],
                        "perfil_investidor_nome": carteira['perfil_investidor']['nome'],                    
                        "transacao_id": transacao['id'],
                        "dt_compra": transacao['dt_compra'],
                        "quantidade_cota": transacao['quantidade_cota'],
                        "preco_cota": transacao['preco_cota'],
                        "valor_investido": transacao['valor_investido'],
                        "tipo_transacao_nome": transacao['tipo_transacao']['nome'] 
                    })     
    return transacoes

@router.get('/transacoes/ativos/{ativo_id}', response_model=List[schemas.Transacao], summary='Obter registros de transações de um ativo')
def obter_transacoes_ativo(token: Annotated[str, Depends(oauth2_scheme)], ativo_id: str):
    """
    Obtém as transações de um ativo
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    session = db_session()   
    transacoes = (session.execute(select(models.Transacao).where(models.Transacao.ativo_id == ativo_id))).scalars().all() 
    return transacoes 
 
@router.delete('/transacoes/{transacao_id}',  summary='Exclui um registro de transação do ativo', include_in_schema=False)
def excluir_transacao(token: Annotated[str, Depends(oauth2_scheme)], transacao_id: str):
    """
    Exclui uma transação de um ativo
    """    
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    session = db_session()   
    try:
        session.execute(delete(models.Transacao).where(models.Transacao.id==transacao_id ))    
        session.commit()       
    except:
        return False
    return True