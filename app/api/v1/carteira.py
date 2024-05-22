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

# Requisições da api de carteiras

from fastapi import APIRouter, Request, status, HTTPException, Depends
from app.database import db_session
from app import models, schemas
from typing import List, Annotated 
from app.libs.security import oauth2_scheme, check_access, usuario_logado
import uuid
from sqlalchemy import select, delete, update
from app.libs.utils import populate

router = APIRouter(prefix='/api/v1', tags=['carteiras'])

@router.post('/carteiras', summary='Criar um registro de carteira do usuário', include_in_schema=False)
async def cadastrar_carteira(token: Annotated[str, Depends(oauth2_scheme)], carteira: schemas.Carteira, request: Request): # pragma: no cover
    """
    Cria um registro de carteira do usuário
    """    
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    usuario = usuario_logado(token)
    carteira.id = str(uuid.uuid4())
    carteira.usuario_id = usuario['usuario_id']
    classes_ativos = carteira.classes_ativos
    del carteira.classes_ativos
    del carteira.perfil_investidor
    del carteira.moeda
    carteira_db = models.Carteira(**carteira.model_dump()) 
    session = db_session()
    session.add(carteira_db)
    session.commit() 
    session.refresh(carteira_db) 
    for classe_ativo in classes_ativos:
        ativos = classe_ativo.ativos
        classe_ativo = classe_ativo.dict()
        classe_ativo.pop('grupo_ativo')
        classe_ativo.pop('ativos') 
        classe_ativo_db = models.ClasseAtivo(**classe_ativo)
        classe_ativo_db.carteira_id = carteira_db.id # FK
        session.add(classe_ativo_db)
        session.commit()
        for ativo in ativos:
            del ativo.tipo_ativo
            del ativo.setor            
            del ativo.moeda            
            ativo_db = models.Ativo(**ativo.dict())
            session.add(ativo_db)
            session.commit() 
    return carteira.id
 
@router.put('/carteiras/{carteira_id}', summary='Atualizar um registro de carteira do usuário', include_in_schema=False) 
def atualizar_carteira(token: Annotated[str, Depends(oauth2_scheme)], carteira_id: str, carteira: schemas.Carteira, request: Request): # pragma: no cover
    """
    Atualiza um registro de carteira do usuário
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    session = db_session()   

    # Obtém as classes de ativos e ativos existentes no banco de dados
    classes_ativos_db = (session.execute(select(models.ClasseAtivo).where(models.ClasseAtivo.carteira_id == carteira_id))).scalars().all()
    if not classes_ativos_db:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Carteira inválida.")    
    classes_ativos_ids = []
    ativos_ids = []
    for classe_ativo_db in classes_ativos_db:
        classes_ativos_ids.append(classe_ativo_db.id)
        for ativo_db in classe_ativo_db.ativos:
            ativos_ids.append(ativo_db.id)
 
    # Percorre as classes de ativos e ativos que estavam na tela do usuário
    if 'classes_ativos' in carteira:
        carteira_classes_ativos = carteira.classes_ativos
        for classes_ativos in carteira_classes_ativos:

            ### ATIVOS       
            classes_ativos_ativos = classes_ativos.ativos
            for ativos in classes_ativos_ativos: 
                del ativos.tipo_ativo
                del ativos.setor
                del ativos.moeda
                del ativos.transacoes
                # Se o ativo já existir no banco de dados, então atualiza
                if ativos.id in ativos_ids:  
                    session.execute(update(models.Ativo).where(models.Ativo.id == ativos.id).values(**ativos.model_dump(exclude_unset=True)))
                    ativos_ids.remove(ativos.id)  

                # Se o ativo não existir no banco, então cria 
                else:
                    ativos_db = models.Ativo(**ativos.model_dump(exclude_unset=True))
                    session.add(ativos_db)

            ### CLASSE DE ATIVOS
            del classes_ativos.grupo_ativo
            del classes_ativos.ativos

            # Se a classe de ativo já existir no banco de dados, então atualiza
            if classes_ativos.id in classes_ativos_ids:
                session.execute(update(models.ClasseAtivo).where(models.ClasseAtivo.id == classes_ativos.id).values(**classes_ativos.model_dump(exclude_unset=True)))
                classes_ativos_ids.remove(classes_ativos.id)  

            # Se a classe de ativo não existir no banco, então cria 
            else:          
                classes_ativos_db = models.ClasseAtivo(**classes_ativos.model_dump(exclude_unset=True))
                session.add(classes_ativos_db)

        # Exclui ativo e transações que estavam no banco, mas que foram excluídos da tela do usuário
        for ativo_id in ativos_ids:
            session.execute(delete(models.Transacao).where(models.Transacao.ativo_id==ativo_id))  
            session.execute(delete(models.Ativo).where(models.Ativo.id==ativo_id))  

        # Remove classes de ativos que estavam no banco, mas qie foi excluída da tela do usuário
        for classe_ativo_id in classes_ativos_ids:
            session.execute(delete(models.ClasseAtivo).where(models.ClasseAtivo.id==classe_ativo_id))  

    # Atualiza a carteira
    del carteira.classes_ativos
    del carteira.perfil_investidor
    session.execute(update(models.Carteira).where(models.Carteira.id == carteira_id).values(**carteira.model_dump(exclude_unset=True)))
    session.commit()       
    return carteira  

@router.delete('/carteiras/{carteira_id}', summary='Excluir um registro de carteira do usuário')
def excluir_carteira(token: Annotated[str, Depends(oauth2_scheme)], carteira_id: str, request: Request): 
    """
    Exclui um registro de carteira do usuário
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])    
    session = db_session()   
    try:
        # Remove ativos e transações
        classes_ativos_db = (session.execute(select(models.ClasseAtivo).where(models.ClasseAtivo.carteira_id == carteira_id))).scalars().all()
        for classe_ativo in classes_ativos_db:        
            for ativo in classe_ativo.ativos:
                for transacao in ativo.transacoes: 
                    session.execute(delete(models.Transacao).where(models.Transacao.id==transacao.id ))    
                session.execute(delete(models.Ativo).where(models.Ativo.classe_ativo_id==ativo.classe_ativo_id ))    
    
        # Remove classes de ativos 
        for classe_ativo in classes_ativos_db:        
            session.execute(delete(models.ClasseAtivo).where(models.ClasseAtivo.carteira_id==carteira_id))   

        session.execute(delete(models.Carteira).where(models.Carteira.id==carteira_id))
        session.commit()      
    except:
        return False
    return True

@router.get('/carteiras/usuarios/{usuario_id}', response_model=List[schemas.Carteira], summary='Obter todos os registros de carteira do usuário')
def obter_carteiras(token: Annotated[str, Depends(oauth2_scheme)], usuario_id: str, request: Request):    
    """
    Obtém todos os registros de carteira do usuário
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    usuario = usuario_logado(token)
 
    # Somente retorna a carteira se for do próprio usuário logado 
    if 'usuario_id' not in usuario or usuario_id != usuario['usuario_id']:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operação não permitida. Autenticação requerida!")   
    session = db_session()
    carteiras = session.execute(select(models.Carteira).where(models.Carteira.usuario_id == usuario_id)).scalars().all()
    return carteiras 

@router.get('/carteiras/{carteira_id}/usuarios/{usuario_id}', response_model=schemas.Carteira, summary='Obter todos os registros de uma carteira do usuário')
# @router.get('/carteiras/{carteira_id}/usuarios/{usuario_id}', summary='Obter todos os registros de uma carteira do usuário')
def obter_carteira(token: Annotated[str, Depends(oauth2_scheme)], carteira_id: str, usuario_id: str, request: Request):   
    """
    Obtém todos os registros de uma carteira do usuário
    """
    check_access(token, ['USER_ADMIN', 'USER_APP'])
    usuario = usuario_logado(token)

    # Somente retorna a carteira se for do próprio usuário logado
    if 'usuario_id' not in usuario or usuario_id != usuario['usuario_id']:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operação não permitida. Autenticação requerida!")        

    session = db_session()
    carteiras = session.execute(select(models.Carteira).where(models.Carteira.usuario_id == usuario_id, models.Carteira.id == carteira_id)).scalars().first()
    return carteiras if carteiras else schemas.Carteira