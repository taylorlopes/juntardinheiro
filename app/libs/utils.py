
"""
Copyright (c) All Rights Reserved 

THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED 
IN THIS NOTICE BE LIABLE FOR ANY CLAIM OR CONSEQUENTIAL DAMAGES OR ANY 
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE DATA OR PROFITS, WHETHER
IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

Author Taylor Lopes <taylorlopes@gmail.com>
""" 

# Funções genéricas e úteis à aplicação

import re
import bcrypt
from datetime import datetime, timezone


def to_dict(obj):
    """
    Converte um objeto scallar do SQLAlchemy para dictionary
    """
    dict_ = []
    for row in obj:   
        dict_.append(dict([(k, getattr(row, k)) for k in row.__dict__.keys() if not k.startswith("_")]))
    return dict_


def obj2dict(obj):
    """
    Converte atributos do objeto/classe para dicionário (dict)

    @param object Objeto (classe Models) a ser convertido em dict
    """
    param_string = str(obj()) 
    matches = re.findall(r'\w+\((.+)\)', param_string) 
    re.sub(r'(\w+)=', r'"\1"=', matches[0])
    return eval(f"dict({matches[0]})")


def populate(el1, el2, overwrite = False): 
    """    
    Popula elemento 1 (el1) com os dados do elemnto 2 (el2)

    @param object|dict el1
    @param object|dict el2
    @param bool overwrite Se False não sobrescre el1 se el2 for None
    @return dict Sempre retorna dict e nunca alterar os objetos de entrada
    """    
    p = {}    
    e1 = el1 if el1.__class__ == dict else obj2dict(el1)
    e2 = el2 if el2.__class__ == dict else obj2dict(el2)
    for k in e1: 
        if overwrite:
            p[k] = e2[k] if k in e2 else None
        else:
            p[k] = e2[k] if k in e2 and e2[k] is not None else e1[k]
    return p


def uncapitalize(s):
    """
    Deixa a primeira letra de uma string sempre em minúscula
    """    
    return s[0].lower() + s[1:] 


def uf():
    """
    Siglas e nomes das Unidades Federativas (UF) do Brasil
    """      
    uf = (
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espirito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MS', 'Mato Grosso do Sul'),
        ('MT', 'Mato Grosso'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins')
        )   
    return uf


def get_words(text, max_chars):
    """
        Obtém apenas palavras inteiras de um texto (text)
        até uma quantidade máxima de caracteres (max_chars),
        eliminando preposição/artigo do final do texto, se houver

        @param str text Texto a ser truncado
        @param int max_chars Quantidade máxima de caracteres
    """    
    if len(text) > max_chars:
        text_ = ' '.join(text.split(' ')[:-1])
        if text_:
            return get_words(text_, max_chars)
        else:
            return text[0:max_chars]
    else:
        if text.split(' ')[-1] in {'da', 'de', 'do', 'a', 'e', 'o'}:
            return ' '.join(text.split(' ')[:-1])
        return text
    
# def get_hashed_password(plain_text_password):
#     # Hash a password for the first time
#     #   (Using bcrypt, the salt is saved into the hash itself)
#     return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())

# def check_password(plain_text_password, hashed_password):
#     # Check hashed password. Using bcrypt, the salt is saved into the hash itself
#     return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))    

def password_check(pwd):     
    return {"check": True, "detail": "Senha válida!"}

    SpecialSym =['$', '@', '#', '%', '!', '&', '*']     
    if len(pwd) < 6:
        return {"check": False, "detail": "A senha deve ter ao menos 6 dígitos"}         
    if len(pwd) > 20:
        return {"check": False, "detail": "A senha deve ter até 20 dígitos"}          
    if not any(char.isdigit() for char in pwd):
        return {"check": False, "detail": "A senha deve ter ao menos um número"}         
    if not any(char.isupper() for char in pwd):
        return {"check": False, "detail": "A senha deve ter um caracter maiúsculo"}         
    if not any(char.islower() for char in pwd):
        return {"check": False, "detail": "A senha deve ter um caracter minúsculo"}            
    if not any(char in SpecialSym for char in pwd):
        return {"check": False, "detail": "A senha deve ter um caracter $@#%&*"}     
    return {"check": True, "detail": "Senha válida!"}
 

def currency_db(value):
    return float(re.sub(r"[^\d,]", '', value, 0, re.DOTALL).replace(',', '.'))

def check_date(year, month, day):
    if len(str(0+int(year))) != 4:
        return False
    try:         
        datetime(int(year), int(month), int(day))
        return True
    except ValueError:
        return  False     

def date_db(input_date):
    day, month, year = input_date[0:11].strip().split('/')
    if not check_date(year, month, day):
        return ''
    output_date = input_date.strip()
    if re.match('^\d{2}\/\d{2}\/\d{4}$', input_date):
        input_date_obj = datetime.strptime(input_date, "%d/%m/%Y")
        output_date = input_date_obj.strftime("%Y-%m-%d")
    elif re.match('^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}$', input_date):
        input_date_obj = datetime.strptime(input_date, "%d/%m/%Y %H:%M:%S")
        output_date = input_date_obj.strftime("%Y-%m-%d %H:%M:%S")
    elif re.match('^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$', input_date):
        input_date_obj = datetime.strptime(input_date, "%d/%m/%Y %H:%M")
        output_date = input_date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return output_date
