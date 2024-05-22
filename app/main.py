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

# Entrada da aplicação

from fastapi import FastAPI, Request
from dotenv import load_dotenv 
from fastapi.staticfiles import StaticFiles 
from app.web import pages
from app.api.v1 import login 
from app.api.v1 import usuario 
from app.api.v1 import carteira 
from app.api.v1 import ativo
from app.api.v1 import transacao
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

load_dotenv()    
app = FastAPI(title='Juntar Dinheiro', swagger_ui_parameters={"defaultModelsExpandDepth": -1})

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Rotas da aplicação
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.include_router(pages.router)
app.include_router(login.router) 
app.include_router(usuario.router)
app.include_router(carteira.router)
app.include_router(ativo.router)
app.include_router(transacao.router)
 
# Cria rota estática para diretório /htmlcov  (relatório do teste de cobertura)
app.mount("/tests", StaticFiles(directory="tests/htmlcov", html=True), name="report-test")
