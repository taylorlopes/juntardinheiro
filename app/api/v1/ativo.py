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

# Requisições da api de ativos

from fastapi import APIRouter
import requests
 
router = APIRouter(prefix='/api/v1', tags=['ativos']) 

@router.get('/ativos', summary='Obter informações do mercado financieiro com base no ticker do ativo')
def obter_ticker(ticker: str | None):  
    """
    Obtém informações do mercado financieiro com base no ticker do ativo
    """  
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    r = requests.get(f'https://statusinvest.com.br/home/mainsearchquery?q={ticker}', headers=headers)
    ativos = r.json()
    suggestions = []
    for ativo in ativos:
        suggestions.append({
            "value": f"{ativo['code']} - {ativo['name']}", 
            "data": {
                "ativo_ticker": ativo['code'], 
                "ativo_nome": ativo['name'],                 
                "ativo_price": ativo['price']
            }
        })
    return {"suggestions": suggestions}  