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

# Configuração Geral

#APP
URL_BASE = 'https://juntardinheiro.com:8000'

# Time Zone
APP_TIME_ZONE = "America/Sao_Paulo"
 
# JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # minutos
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 dias
ALGORITHM = "HS256"