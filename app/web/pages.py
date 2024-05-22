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

# Rotas para as páginas estáticas da aplicação

from fastapi import APIRouter, Request, Response 
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates 
from app.libs.security import check_access, usuario_logado
from app.libs.utils import to_dict 
from sqlalchemy import select
from app.database import db_session
from app import models, schemas
import requests
import app.config as config
from datetime import datetime  
import pytz  
import json
import uuid

templates = Jinja2Templates(directory="app/web/templates")  

router = APIRouter(include_in_schema=False) 
 
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Exibe a tela inicial da aplicação
    """
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token)    
    return templates.TemplateResponse(request, "index.html", {"usuario": usuario})

@router.get("/tests", response_class=HTMLResponse)
def home(request: Request):
    """
    Exibe a tela de testes de unidade/cobertu4ra
    """ 
    return templates.TemplateResponse(request, "htmlcov/index.html")

@router.get("/login", response_class=HTMLResponse)
def login(request: Request):    
    """
    Exibe a tela de login
    """   
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token)
    try:        
        check_access(token, ['USER_ADMIN', 'USER_APP'])     
    except:
        return templates.TemplateResponse(request, "login.html", {"usuario": usuario})
    return RedirectResponse("/painel")        

@router.get("/usuario-novo", response_class=HTMLResponse)
def usuario_novo(request: Request):
    """
    Exibe a tela de cadastro de novo usuário
    """    
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token)
    return templates.TemplateResponse(request, "usuario-novo.html", {"usuario": usuario})

@router.get("/tema/", response_class=RedirectResponse)
def tema(request: Request, response: Response, url: str):    
    """
    Troca o tema da aplicação
    """
    theme = 'dark' if request.cookies.get('theme') == 'light' else 'light'
    r = RedirectResponse(url, status_code=303)
    r.set_cookie(key="theme", value=theme, expires = 12 * 30 * 24 * 60 * 60 )
    return r

@router.get("/painel", response_class=HTMLResponse)
def painel(request: Request): 
    """
    Exibe o painel do usuário logado
    """     
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token)    
    try:
        check_access(token, ['USER_ADMIN', 'USER_APP'])
    except:
        return RedirectResponse("/login")  
    r = requests.get(url=f"{config.URL_BASE}/api/v1/carteiras/usuarios/{usuario['usuario_id']}",                      
                     headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"},
                     verify=False)
    carteiras = json.loads(r.text)
    total_carteira = 0
    total_rf = 0
    total_rv = 0
    for carteira in carteiras:
        moeda_preferencial_codigo = carteira['moeda']['codigo']
        moeda_preferencial_simbolo = carteira['moeda']['simbolo']
        carteira['valores'] = {}
        carteira['total_valor_convertido'] = 0
        carteira['valores_rf'] = {}
        carteira['valores_rv'] = {}
        carteira['total_valor_convertido_rf'] = 0
        carteira['total_valor_convertido_rv'] = 0
        for classe_ativo in carteira['classes_ativos']:
            classe_ativo['valores'] = {}
            classe_ativo['total_valor_convertido'] = 0
            for ativo in classe_ativo['ativos']:
                total_cota = 0
                total_valor = 0
                moeda = ativo['moeda']['simbolo']
                moeda_codigo = ativo['moeda']['codigo']
                total_valor_convertido = 0
                for transacao in ativo['transacoes']:                    
                    if transacao['tipo_transacao_id'] == 1:
                        total_carteira += transacao['valor_investido'] 
                        total_cota += transacao['quantidade_cota']
                        total_valor += transacao['valor_investido'] 
                    else:                        
                        total_carteira -= transacao['valor_investido'] 
                        total_cota -= transacao['quantidade_cota']
                        total_valor -= transacao['valor_investido']                      
                    if  moeda_codigo != moeda_preferencial_codigo:
                        url = f'https://economia.awesomeapi.com.br/{moeda_codigo}-{moeda_preferencial_codigo}/0'
                        r = requests.get(url)
                        v = json.loads(r.text)
                        v = float(v[0]['bid'])
                        total_valor_convertido += v * total_valor
                ativo.update({"total_cota":  total_cota})
                ativo.update({"total_valor":  total_valor})
                ativo.update({"simbolo_convertido": moeda_preferencial_simbolo})             
                ativo.update({"total_valor_convertido": total_valor_convertido if total_valor_convertido > 0 else 0})

                # Totalização da carteira
                carteira_valores = 0 if moeda not in carteira['valores'] else carteira['valores'][moeda]
                carteira["valores"].update({moeda: carteira_valores + total_valor})
                carteira.update({"simbolo_convertido": moeda_preferencial_simbolo})
                carteira.update({"total_valor_convertido": (carteira['total_valor_convertido'] + total_valor_convertido) if total_valor_convertido > 0 else (carteira['total_valor_convertido'] + total_valor)})
             
                # Totalização do grupo de ativos
                if classe_ativo["grupo_ativo_id"] == 1:
                    carteira_valores_rf = 0 if moeda not in carteira['valores_rf'] else carteira['valores_rf'][moeda]
                    carteira["valores_rf"].update({moeda: carteira_valores_rf + total_valor})
                    carteira.update({"total_valor_convertido_rf": (carteira['total_valor_convertido_rf'] + total_valor_convertido) if total_valor_convertido > 0 else (carteira['total_valor_convertido_rf'] + total_valor)})

                if classe_ativo["grupo_ativo_id"] == 2:
                    carteira_valores_rv = 0 if moeda not in carteira['valores_rv'] else carteira['valores_rv'][moeda]
                    carteira["valores_rv"].update({moeda: carteira_valores_rv + total_valor})
                    carteira.update({"total_valor_convertido_rv": (carteira['total_valor_convertido_rv'] + total_valor_convertido) if total_valor_convertido > 0 else (carteira['total_valor_convertido_rv'] + total_valor)})

                # Totalização da classe ativos
                classe_ativo_valores = 0 if moeda not in classe_ativo['valores'] else classe_ativo['valores'][moeda]
                classe_ativo["valores"].update({moeda: classe_ativo_valores + total_valor})
                classe_ativo.update({"simbolo_convertido": moeda_preferencial_simbolo})
                classe_ativo.update({"total_valor_convertido": (classe_ativo['total_valor_convertido'] + total_valor_convertido) if total_valor_convertido > 0 else (classe_ativo['total_valor_convertido'] + total_valor)})
 
    if not carteiras:
        return RedirectResponse("/carteiras")

    carteiras_classes_ativos = {}
    for carteira in carteiras: 
        carteiras_rf = []
        carteiras_rv = []        
        categories_rf = []
        categories_rv = []
        data_rf = []
        data_rv = []        
        for classe_ativo in carteira["classes_ativos"]:
            if classe_ativo["grupo_ativo_id"] == 1:
                categories_rf.append(classe_ativo["nome"])
                data_rf.append(classe_ativo["percentual"])
            elif classe_ativo["grupo_ativo_id"] == 2:
                categories_rv.append(classe_ativo["nome"])
                data_rv.append(classe_ativo["percentual"])
        carteiras_rf.append({
            carteira['id'] : {
                "y": carteira["renda_fixa_percentual"],
                "color": "#0B5ED7",
                "drilldown": {
                    "name": 'Renda Fixa',
                    "categories": categories_rf,
                    "data": data_rf
                }                        
            }                    
        })
        carteiras_rv.append({
            carteira['id'] : {
                "y": carteira["renda_variavel_percentual"],
                "color": "#e83b31",
                "drilldown": {
                    "name": 'Renda Variável',
                    "categories": categories_rv,
                    "data": data_rv
                }                        
            }                    
        }) 
        carteiras_classes_ativos[carteira['id']] = {"carteiras_rf": carteiras_rf, "carteiras_rv": carteiras_rv} 
    session = db_session()
    tipos_transacoes = to_dict(session.execute(select(models.TipoTransacao)).scalars().all())
    return templates.TemplateResponse(request, "painel.html", {
        "token": token, 
        "usuario": usuario, 
        "carteiras": carteiras, 
        "carteiras_classes_ativos": carteiras_classes_ativos,
        "tipos_transacoes": tipos_transacoes,
        "data_atual": datetime.now(pytz.timezone(config.APP_TIME_ZONE)).strftime("%Y-%m-%d"),
        "total_carteira": total_carteira,
        "total_rf": total_rf,
        "total_rv": total_rv    
    })

@router.get("/carteiras", response_class=HTMLResponse)
def carteira_nova(request: Request): 
    """
    Exibe a tela para criar nova carteira
    """    
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token)
    try:
        check_access(token, ['USER_ADMIN', 'USER_APP'])
    except:
        return RedirectResponse("/login")
    session = db_session()
    grupos_ativos = to_dict(session.execute(select(models.GrupoAtivo)).scalars().all())
    perfis_investidores = to_dict(session.execute(select(models.PerfilInvestidor)).scalars().all())
    tipos_ativos = to_dict(session.execute(select(models.TipoAtivo)).scalars().all())
    setores = to_dict(session.execute(select(models.Setor)).scalars().all())
    moedas = to_dict(session.execute(select(models.Moeda)).scalars().all())

    # Monta carteira default (carrega dados de exemplo de carteira)
    with open('./app/web/carteira.json') as f:
        carteira =  f.read() 
    ca1 = str(uuid.uuid4())
    ca2 = str(uuid.uuid4())
    ca3 = str(uuid.uuid4())
    ca4 = str(uuid.uuid4())
    ca5 = str(uuid.uuid4())
    ca6 = str(uuid.uuid4())
    carteira = carteira.replace("{CA_1}", ca1)
    carteira = carteira.replace("{CA_2}", ca2)
    carteira = carteira.replace("{CA_3}", ca3)
    carteira = carteira.replace("{CA_4}", ca4)
    carteira = carteira.replace("{CA_5}", ca5)
    carteira = carteira.replace("{CA_6}", ca6)
    carteira = carteira.replace("{AT_1}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_2}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_3}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_4}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_5}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_6}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_7}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_8}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_9}", str(uuid.uuid4()))
    carteira = carteira.replace("{AT_10}", str(uuid.uuid4()))    
    carteira = json.loads(carteira)    

    classes_ativos = carteira['classes_ativos']
    return templates.TemplateResponse(request, "carteira.html", {
        "token": token, 
        "usuario":usuario, 
        "carteira":  carteira, 
        "grupos_ativos": grupos_ativos,
        "perfis_investidores": perfis_investidores,
        "classes_ativos": classes_ativos,
        "tipos_ativos": tipos_ativos,
        "setores": setores,
        "moedas": moedas,
    }) 


@router.get("/carteiras/{carteira_id}/editar", response_class=HTMLResponse)
def carteira_editar(carteira_id: str, request: Request): 
    """
    Exibe a tela para editar carteira
    """    
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token)
    try:
        check_access(token, ['USER_ADMIN', 'USER_APP'])
    except:
        return RedirectResponse("/login")    
    
    r = requests.get(url=f"{config.URL_BASE}/api/v1/carteiras/{carteira_id}/usuarios/{usuario['usuario_id']}",                      
                     headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"},
                     verify=False) 
    carteiras = json.loads(r.text)
    session = db_session()
    grupos_ativos = to_dict(session.execute(select(models.GrupoAtivo)).scalars().all())
    perfis_investidores = to_dict(session.execute(select(models.PerfilInvestidor)).scalars().all())
    tipos_ativos = to_dict(session.execute(select(models.TipoAtivo)).scalars().all())
    setores = to_dict(session.execute(select(models.Setor)).scalars().all())
    moedas = to_dict(session.execute(select(models.Moeda)).scalars().all())
    classes_ativos = carteiras['classes_ativos']
    return templates.TemplateResponse(request, "carteira.html", {
        "token": token, 
        "usuario":usuario, 
        "carteira":carteiras, 
        "grupos_ativos": grupos_ativos,
        "perfis_investidores": perfis_investidores,
        "classes_ativos": classes_ativos,
        "tipos_ativos": tipos_ativos,
        "setores": setores,
        "moedas": moedas
    }) 


@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request): 
    """
    Exibe de logout
    """    
    response = templates.TemplateResponse(request, "index.html",  {"usuario": {}})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@router.get("/altera-senha", response_class=HTMLResponse)
def redefinir_senha(request: Request, email: str | None = ""):    
    """
    Exibe a tela para solicitar a alteração de senha
    """   
    token = request.cookies.get('access_token')
    usuario = usuario_logado(token) if token else {} 
    return templates.TemplateResponse(request, "altera-senha.html", {"usuario": usuario, "email": email, "step": 1})

@router.get("/altera-senha/{token}", response_class=HTMLResponse)
def redefinir_senha(request: Request, token: str):    
    """
    Exibe a tela para trocar senha
    """  
    try:        
        check_access(token, ['USER_ADMIN', 'USER_APP'])     
    except:
        # return templates.TemplateResponse(request, "login.html", {"usuario": usuario})
        return RedirectResponse("/login")        
    return templates.TemplateResponse(request, "altera-senha.html", {"usuario": {}, "token": token, "step": 2})