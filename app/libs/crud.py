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

# Automatiza CRUD

from fastapi import APIRouter, HTTPException 
from app.database import db_session
from sqlmodel import select 
 
class CRUD():
 
    def __init__(self, Entity) -> None:
        self.entity = Entity
    
    def create(self, input, entity_title = None):
        session = db_session()
        session.add(input) 
        session.commit()
        results = session.exec(select(self.entity).order_by((self.entity).id.desc())).first()
        session.close()
        return results   
    
    def read(self, id: int = None, entity_title = None):
        session = db_session()
        if id is None:            
            statement = select(self.entity)
            results = session.exec(statement).all()   
        else:             
            results = session.get(self.entity, id) 
            if not results:
                raise HTTPException(status_code=404, detail=f"Registro de {entity_title} não encontrado.")
        session.close()
        return results    
    
    def update(self, id: int, input, entity_title = None):
        session = db_session()
        results = session.get(self.entity, id)
        if not results:
            raise HTTPException(status_code=404, detail=f"Registro de {entity_title} não encontrado.")
        data = input.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(results, key, value)
        session.add(results)
        session.commit()
        session.refresh(results)
        session.close()
        return results        

    def delete(self, id: int, entity_title = None):
        session = db_session()
        results = session.get(self.entity, id) 
        if not results:
            raise HTTPException(status_code=404, detail=f"Registro de {entity_title} não encontrado.")        
        session.delete(results)
        session.commit()
        session.close()
        return results        

    def router(self, router_prefix: str, entity_name: str, entity_title: str, action: str = 'CRUD'):         
        router = APIRouter(prefix=router_prefix, tags=[entity_name]) 
        if 'C' in action:
            @router.post(f'/{entity_name}', response_model=self.entity, summary=f'Cria um registro de {entity_title}')
            def _create(input: self.entity):
                return CRUD(self.entity).create(input, entity_title)    
        if 'R' in action:
            @router.get(f'/{entity_name}', response_model=list[self.entity], summary=f'Obtém todos os registros de {entity_title}')
            def _read_all():
                return CRUD(self.entity).read(None, entity_title)    
            @router.get(f'/{entity_name}/' + '{id}', response_model=self.entity, summary=f'Obtém um único registro de {entity_title}')
            def _read(id: int):
                return CRUD(self.entity).read(id, entity_title)     
        if 'U' in action:            
            @router.put(f'/{entity_name}/' + '{id}', response_model=self.entity, summary=f'Atualiza um registro de {entity_title}')
            def _update(id: int, input: self.entity):
                return CRUD(self.entity).update(id, input, entity_title)
        if 'D' in action:            
            @router.delete(f'/{entity_name}/' + '{id}', response_model=self.entity, summary=f'Exclui um registro de {entity_title}')
            def _delete(id: int):
                return CRUD(self.entity).delete(id, entity_title)
        return router