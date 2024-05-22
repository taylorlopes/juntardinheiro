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

# Tipagem de dados

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


"""
-------------------------------------------------------------------------------

Auxiliares

-------------------------------------------------------------------------------
"""


class GrupoAtivo(BaseModel):
    id: int    
    nome: str
 
class PerfilInvestidor(BaseModel):
    id: int    
    nome: str

class Setor(BaseModel):
    id: int
    nome: str

class TipoAtivo(BaseModel):    
    id: int
    nome: str
    descricao: str | None 

class Moeda(BaseModel):
    id: int
    codigo: str    
    nome: str    
    simbolo: str    
    regiao: str    


"""
-------------------------------------------------------------------------------

Ativo

-------------------------------------------------------------------------------
"""


class Ativo(BaseModel):
    id: str
    ticker: str
    nome: str | None = None
    cnpj: str | None = None
    percentual: float
    nacional: str | None    
    # original: str | None  = None  
    classe_ativo_id: str
    tipo_ativo_id: int
    setor_id: int 
    moeda_id: int 
    tipo_ativo: TipoAtivo | None  = None  
    setor: Setor | None  = None  
    moeda: Moeda | None  = None  
    transacoes: List["Transacao"] | None = []

"""
-------------------------------------------------------------------------------
Classe de ativos

-------------------------------------------------------------------------------
"""

class ClasseAtivo(BaseModel):
    id: str
    nome: str
    descricao: str | None = None
    percentual: float
    carteira_id: str  | None = None 
    grupo_ativo_id: int   
    grupo_ativo: GrupoAtivo | None = None 
    ativos: List[Ativo] | None = []
        
 

"""
-------------------------------------------------------------------------------

Carteira

-------------------------------------------------------------------------------
"""

class Carteira(BaseModel):
    id: str | None = None
    nome: str | None = None
    renda_fixa_percentual: float | None = None
    renda_variavel_percentual: float | None = None
    perfil_investidor_id: int | None = None
    perfil_investidor: PerfilInvestidor | None = None
    usuario_id: str | None = None
    classes_ativos: List[ClasseAtivo] = []
    moeda_id: int | None = None
    moeda: Moeda | None  = None 


"""
-------------------------------------------------------------------------------

Usuário

-------------------------------------------------------------------------------
""" 

class PerfilSistema(BaseModel):
    id: int    
    nome: str

class Usuario(BaseModel):
    id: str | None = None
    nome: str
    senha: str
    email: str
    dt_cadastro: datetime  | None = None
    dt_ultimo_login: datetime | None = None
    perfis: List[PerfilSistema] = []
    carteiras: List[Carteira] = []

class UsuarioInput(BaseModel):
    nome: str | None = None
    senha: str | None = None
    email: str | None = None
 
class TipoTransacao(BaseModel):
    id: int
    nome: str
 
class Transacao(BaseModel): 
    id: str | None = None
    dt_compra: datetime
    quantidade_cota: float
    preco_cota: float
    valor_investido: float
    outros_custos: float
    valor_total: float 
    ativo_id: str
    tipo_transacao_id: int
    tipo_transacao: TipoTransacao | None = None 