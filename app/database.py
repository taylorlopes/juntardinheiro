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

# Configuração e criação de banco de dados
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html

from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
import os 

def db_url():
    """
    Cria a string de conexão com o banco de dados
    """
    hostname = os.environ.get('MSSQL_HOSTNAME')
    database = os.environ.get('MSSQL_DATABASE')
    username = os.environ.get('MSSQL_USERNAME')
    password = os.environ.get('MSSQL_PASSWORD') 
    SQLALCHEMY_DATABASE_URL = f'mssql+pyodbc://{username}:{password}@{hostname}/{database}?driver=ODBC+Driver+17+for+SQL+Server&MARS_Connection=Yes'
    return SQLALCHEMY_DATABASE_URL 

def db_session():
    """
    Retorna a session do banco de dados
    """
    engine = create_engine(db_url(), echo=False) 
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return Session()

def db_engine():
    """
    Retorna a engine do banco de dados
    """
    engine = create_engine(db_url())
    return engine 

def db_create():
    """
    Cria o banco de dados e tabelas
    """
    import sys
    sys.path.insert(1, '../')    
    from dotenv import load_dotenv 
    from app.libs.security import get_hashed_password
    from datetime import datetime    
    import app.config as config
    import pytz

    from app.models import Usuario
    from app.models import PerfilSistema
    from app.models import usuario_perfil_sistema
    from app.models import PerfilInvestidor
    from app.models import Carteira
    from app.models import GrupoAtivo    
    from app.models import ClasseAtivo
    # from app.models import ClasseAtivoSugerido
    from app.models import TipoAtivo
    from app.models import Setor
    from app.models import Moeda
    from app.models import Ativo
    from app.models import TipoTransacao
    from app.models import Transacao

    from app.models import Base

    load_dotenv()       
    
    Base.metadata.drop_all(bind=db_engine())

    Base.metadata.create_all(bind=db_engine()) 

    session = db_session()
    
    # Registra perfis da aplicação padrão
    perfil_1 = PerfilSistema(id=1, codigo="USER_ADMIN", nome="Admin")
    perfil_2 = PerfilSistema(id=2, codigo="USER_APP", nome="Investidor")    
    session.add(perfil_1)
    session.add(perfil_2)
    session.commit() 

    # Registra usuários padrão
    usuario_1 = Usuario(id="a85755da-9d66-45c3-9419-cea1b4c7d626",                       
                       nome="Taylor Lopes",
                       senha=get_hashed_password('123'),                       
                       email="taylorlopes@gmail.com",
                       dt_cadastro=datetime.now(pytz.timezone(config.APP_TIME_ZONE)),
                       dt_ultimo_login=datetime.now(pytz.timezone(config.APP_TIME_ZONE))) 
    session.add(usuario_1)
    session.commit()
 
    # Vincula usuário ao perfil de sistema
    session.execute(usuario_perfil_sistema.insert().values(usuario_id='a85755da-9d66-45c3-9419-cea1b4c7d626', perfil_sistema_id=1)) 
    session.commit()

    # Registra perfis de investidor padrão
    perfil_investidor_1 = PerfilInvestidor(id=1, nome="Conservador", descricao="Perfil que prioriza segurança e liquidez ao invés de rentabilidade, optando por investimentos de baixo risco. Mantém a maior parte do patrimônito em renda fixa")
    perfil_investidor_2 = PerfilInvestidor(id=2, nome="Moderado", descricao="Perfil que aceita correr algum risco para obter um pouco mais de rentabilidade, mas preza também pela segurança. Concilia investimentos de renda fixa com renda variável")
    perfil_investidor_3 = PerfilInvestidor(id=3, nome="Arrojado", descricao="Perfil com preparo emocional para lidar com as oscilações do mercado, assumindo riscos para obter maior rentabilidade. Concentra a maior parte dos investimentos na renda variável")
    session = db_session()
    session.add(perfil_investidor_1)
    session.add(perfil_investidor_2)
    session.add(perfil_investidor_3)
    session.commit()

    # Registra grupos de ativo padrão
    grupo_ativo_1 = GrupoAtivo(id=1, nome="Renda Fixa", descricao="Investimento de menor risco em títulos públicos ou privados, o que equivale a emprestar dinheiro a uma instituição como banco, empresa ou governo, em que você recebe juros por isso") 
    grupo_ativo_2 = GrupoAtivo(id=2, nome="Renda Variável",  descricao="Investimento de maior risco como ações de empresas, ativos imobiliários, moedas estrangeiras, commodities (ouro, petróleo, soja) e criptomoedas, em que você obtém lucro (ou prejuízo) dele") 
    session = db_session()
    session.add(grupo_ativo_1) 
    session.add(grupo_ativo_2) 
    session.commit()

    # Registra tipos de ativo padrão
    tipo_ativo_1 = TipoAtivo(id=1, nome="A definir", descricao="")
    tipo_ativo_2 = TipoAtivo(id=2, nome="Ações", descricao="")
    tipo_ativo_3 = TipoAtivo(id=3, nome="BDRs", descricao="")
    tipo_ativo_4 = TipoAtivo(id=4, nome="CDBs", descricao="Certificado de Depósito Bancário")
    tipo_ativo_5 = TipoAtivo(id=5, nome="CRAs", descricao="Certificados de Recebíveis do Agronegócio")
    tipo_ativo_6 = TipoAtivo(id=6, nome="CRIs", descricao="Certificados de Recebíveis Imobiliários")    
    tipo_ativo_7 = TipoAtivo(id=7, nome="Criptomoedas", descricao="")    
    tipo_ativo_8 = TipoAtivo(id=8, nome="COEs", descricao="Certificado de Operações Estruturadas")
    tipo_ativo_9 = TipoAtivo(id=9, nome="Commodities", descricao="")
    tipo_ativo_10 = TipoAtivo(id=10, nome="Conta corrente", descricao="")
    tipo_ativo_11 = TipoAtivo(id=11, nome="Debêntures", descricao="")
    tipo_ativo_12 = TipoAtivo(id=12, nome="Derivativos", descricao="")
    tipo_ativo_13 = TipoAtivo(id=13, nome="ETFs", descricao="Exchange Traded Funds")
    tipo_ativo_14 = TipoAtivo(id=14, nome="FIIs", descricao="Fundos de investimento imobiliário")
    tipo_ativo_15 = TipoAtivo(id=15, nome="Fundos de ações", descricao="")
    tipo_ativo_16 = TipoAtivo(id=16, nome="Fundos multimercado", descricao="")
    tipo_ativo_17 = TipoAtivo(id=17, nome="LC", descricao="Letra de Câmbio")
    tipo_ativo_18 = TipoAtivo(id=18, nome="LCI", descricao="Letras de Crédito Imobiliário")
    tipo_ativo_19 = TipoAtivo(id=19, nome="LCA", descricao="Letras de Crédito do Agronegócio")
    tipo_ativo_20 = TipoAtivo(id=20, nome="Poupança", descricao="")
    tipo_ativo_21 = TipoAtivo(id=21, nome="REITs", descricao="")
    tipo_ativo_22 = TipoAtivo(id=22, nome="STOCKS", descricao="")
    tipo_ativo_23 = TipoAtivo(id=23, nome="Tesouro Direto", descricao="")
    session = db_session()
    session.add(tipo_ativo_1) 
    session.add(tipo_ativo_2) 
    session.add(tipo_ativo_3) 
    session.add(tipo_ativo_4) 
    session.add(tipo_ativo_5) 
    session.add(tipo_ativo_6) 
    session.add(tipo_ativo_7) 
    session.add(tipo_ativo_8) 
    session.add(tipo_ativo_9) 
    session.add(tipo_ativo_10) 
    session.add(tipo_ativo_11) 
    session.add(tipo_ativo_12) 
    session.add(tipo_ativo_13) 
    session.add(tipo_ativo_14) 
    session.add(tipo_ativo_15) 
    session.add(tipo_ativo_16) 
    session.add(tipo_ativo_17) 
    session.add(tipo_ativo_18) 
    session.add(tipo_ativo_19) 
    session.add(tipo_ativo_20) 
    session.add(tipo_ativo_21) 
    session.add(tipo_ativo_22) 
    session.add(tipo_ativo_23) 
    session.commit()

    # Registra setores de ativos padrão
    setor_1 = Setor(id=1, nome="A definir")
    setor_2 = Setor(id=2, nome="Agronegócio")
    setor_3 = Setor(id=3, nome="Alimentos e Bebidas")
    setor_4 = Setor(id=4, nome="Comunicações")
    setor_5 = Setor(id=5, nome="Consumo Cíclico")
    setor_6 = Setor(id=6, nome="Consumo não Cíclico")
    setor_7 = Setor(id=7, nome="Bens de Capital")
    setor_8 = Setor(id=8, nome="Bens Industriais")
    setor_9 = Setor(id=9, nome="Educação")
    setor_10 = Setor(id=10, nome="Energia")
    setor_11 = Setor(id=11, nome="Financeiro e Bancário")
    setor_12 = Setor(id=12, nome="Imobiliário")
    setor_13 = Setor(id=13, nome="Imobiliário - Dívidas")
    setor_14 = Setor(id=14, nome="Imobiliário - Educacional")
    setor_15 = Setor(id=15, nome="Imobiliário - Fundo de Fundos")    
    setor_16 = Setor(id=16, nome="Imobiliário - Híbrido")  
    setor_17 = Setor(id=17, nome="Imobiliário - Hotéis")
    setor_18 = Setor(id=18, nome="Imobiliário - Lajes Corporativas")
    setor_19 = Setor(id=19, nome="Imobiliário - Logístico")
    setor_20 = Setor(id=20, nome="Imobiliário - Saúde")
    setor_21 = Setor(id=21, nome="Imobiliário - Recebíveis")  
    setor_22 = Setor(id=22, nome="Imobiliário - Rural")  
    setor_23 = Setor(id=23, nome="Imobiliário - Shopping")  
    setor_24 = Setor(id=24, nome="Materiais Básicos")
    setor_25 = Setor(id=25, nome="Mineração e Siderurgia")
    setor_26 = Setor(id=26, nome="Outros")
    setor_27 = Setor(id=27, nome="Papel e Celulose")
    setor_28 = Setor(id=28, nome="Petróleo, Gás e Biocombustíveis")
    setor_29 = Setor(id=29, nome="Saneamento")
    setor_30 = Setor(id=30, nome="Saúde")
    setor_31 = Setor(id=31, nome="Tecnologia da Informação e Telecomunicações")
    setor_32 = Setor(id=32, nome="Transportes")
    setor_33 = Setor(id=33, nome="Utilidade Pública")
    setor_34 = Setor(id=34, nome="Varejo")
    setor_35 = Setor(id=35, nome="Câmbio e Moeda")
    session = db_session() 
    session.add(setor_1) 
    session.add(setor_2) 
    session.add(setor_3) 
    session.add(setor_4) 
    session.add(setor_5) 
    session.add(setor_6) 
    session.add(setor_7) 
    session.add(setor_8) 
    session.add(setor_9) 
    session.add(setor_10) 
    session.add(setor_11) 
    session.add(setor_12) 
    session.add(setor_13) 
    session.add(setor_14) 
    session.add(setor_15) 
    session.add(setor_16) 
    session.add(setor_17) 
    session.add(setor_18) 
    session.add(setor_19) 
    session.add(setor_20) 
    session.add(setor_21)  
    session.add(setor_22)  
    session.add(setor_23)  
    session.add(setor_24)  
    session.add(setor_25)  
    session.add(setor_26)  
    session.add(setor_27)  
    session.add(setor_28)  
    session.add(setor_29)  
    session.add(setor_30)  
    session.add(setor_31)  
    session.add(setor_32)      
    session.add(setor_33)      
    session.add(setor_34)      
    session.add(setor_35)      
    session.commit() 
 
    # Registra tipos de transação padrão
    tipo_transacao_1 = TipoTransacao(id=1, nome="Compra")
    tipo_transacao_2 = TipoTransacao(id=2, nome="Venda")    
    session = db_session()
    session.add(tipo_transacao_1)
    session.add(tipo_transacao_2) 
    session.commit()

    # Registra moedas
    sql="""INSERT INTO moeda (id, codigo, nome, simbolo, regiao) VALUES
        (1, 'BRL', 'Real Brasileiro', 'R$', 'Brasil'),
        (2, 'USD', 'Dólar americano', '$', 'Estados Unidos'),
        (3, 'EUR', 'Euro', '€', 'Países da Zona do Euro'),
        (4, 'JPY', 'Iene', '¥', 'Japão'),
        (5, 'GBP', 'Libra Esterlina', '£', 'Reino Unido'),
        (6, 'CHF', 'Franco Suíço', 'SFr', 'Suíça'),
        (7, 'CAD', 'Dólar Canadense', 'C$', 'Canadá'),
        (8, 'AUD', 'Dólar Australiano', 'A$', 'Austrália'),
        (9, 'ZAR', 'Rand', 'R', 'África do Sul'),
        (10, 'CNY', 'Yuan', '¥', 'China'),
        (11, 'ARS', 'Peso Argentino', '$', 'Argentina')
    """
    session.execute(text(sql)) 
    session.commit()

    print('Banco de dados e tabelas criados.')    

if __name__ == "__main__":
    db_create()