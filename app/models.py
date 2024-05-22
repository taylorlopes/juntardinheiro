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

# Modelagem de dados - ORM

from __future__ import annotations
from decimal import Decimal
from typing import List
from typing import Optional
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Numeric 
from sqlalchemy import DateTime
from sqlalchemy import Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import Optional, List
from pydantic import validator
from fastapi import  HTTPException
from app.libs.utils import password_check
import app.config as config
from datetime import datetime
import pytz
import re

class Base(DeclarativeBase):
    pass

usuario_perfil_sistema = Table(
    "usuario_perfil_sistema",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuario.id")),
    Column("perfil_sistema_id", ForeignKey("perfil_sistema.id")),
)

class Usuario(Base):
    __tablename__ = "usuario"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    senha: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    dt_cadastro: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now(pytz.timezone(config.APP_TIME_ZONE)))
    dt_ultimo_login: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now(pytz.timezone(config.APP_TIME_ZONE)))
    perfis: Mapped[List["PerfilSistema"]] = relationship(secondary=usuario_perfil_sistema)
    carteiras: Mapped[List["Carteira"]] = relationship()
    
class PerfilSistema(Base):
    __tablename__ = "perfil_sistema"
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)

class PerfilInvestidor(Base):
    __tablename__ = "perfil_investidor"
    id: Mapped[int] = mapped_column(primary_key=True)    
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str] = mapped_column(String(500), nullable=True)

class Carteira(Base):
    __tablename__ = "carteira"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    renda_fixa_percentual: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    renda_variavel_percentual: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    perfil_investidor_id: Mapped[int] = mapped_column(ForeignKey("perfil_investidor.id"))
    moeda_id: Mapped[int] = mapped_column(ForeignKey("moeda.id"),  default=1)    
    perfil_investidor: Mapped["PerfilInvestidor"] = relationship()
    classes_ativos: Mapped[List["ClasseAtivo"]] = relationship()    
    moeda: Mapped["Moeda"] = relationship()  

class GrupoAtivo(Base):
    __tablename__ = "grupo_ativo"
    id: Mapped[int] = mapped_column(primary_key=True)    
    nome: Mapped[str] = mapped_column(String(50), nullable=False)    
    descricao: Mapped[str] = mapped_column(String(500), nullable=True)
  
class ClasseAtivo(Base):
    __tablename__ = "classe_ativo"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(String(500), nullable=True)
    percentual: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    carteira_id: Mapped[str] = mapped_column(ForeignKey("carteira.id"))
    grupo_ativo_id: Mapped[int] = mapped_column(ForeignKey("grupo_ativo.id"))  
    grupo_ativo: Mapped["GrupoAtivo"] = relationship()
    ativos: Mapped[List["Ativo"]] = relationship() 

class Ativo(Base):
    __tablename__ = "ativo"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=True)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=True)
    percentual: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    nacional: Mapped[str] = mapped_column(String(1), default='1', nullable=False)
    # original: Mapped[str] = mapped_column(String(1), default='1', nullable=True)
    classe_ativo_id: Mapped[str] = mapped_column(ForeignKey("classe_ativo.id"))
    # carteira_id: Mapped[str] = mapped_column(ForeignKey("carteira.id"))
    tipo_ativo_id: Mapped[int] = mapped_column(ForeignKey("tipo_ativo.id"))
    setor_id: Mapped[int] = mapped_column(ForeignKey("setor.id"))
    moeda_id: Mapped[int] = mapped_column(ForeignKey("moeda.id"),  default=1)
    tipo_ativo: Mapped["TipoAtivo"]  = relationship()
    setor: Mapped["Setor"]  = relationship()
    moeda: Mapped["Moeda"]  = relationship()
    transacoes: Mapped[List["Transacao"]]  = relationship()

class Setor(Base):
    __tablename__ = "setor"
    id: Mapped[int] = mapped_column(primary_key=True)    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)    

class TipoAtivo(Base):
    __tablename__ = "tipo_ativo"
    id: Mapped[int] = mapped_column(primary_key=True)    
    nome: Mapped[str] = mapped_column(String(100), nullable=False)   
    descricao: Mapped[str] = mapped_column(String(500), nullable=True) 

class Moeda(Base):
    __tablename__ = "moeda"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)    
    codigo: Mapped[str] = mapped_column(String(3), nullable=False)       
    nome: Mapped[str] = mapped_column(String(50), nullable=False)       
    simbolo: Mapped[str] = mapped_column(String(50), nullable=False)    
    regiao: Mapped[str] = mapped_column(String(50), nullable=False)              

class TipoTransacao(Base):
    __tablename__ = "tipo_transacao"
    id: Mapped[int] = mapped_column(primary_key=True)    
    nome: Mapped[str] = mapped_column(String(50), nullable=False)   
 
class Transacao(Base):
    __tablename__ = "transacao"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dt_compra: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now(pytz.timezone(config.APP_TIME_ZONE)))
    quantidade_cota: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    preco_cota: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0.00, nullable=False)
    valor_investido: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0.00, nullable=False)
    outros_custos: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0.00, nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0.00, nullable=False)
    ativo_id: Mapped[str] = mapped_column(ForeignKey("ativo.id"))    
    tipo_transacao_id: Mapped[int] = mapped_column(ForeignKey("tipo_transacao.id"))
    tipo_transacao: Mapped["TipoTransacao"]  = relationship()


