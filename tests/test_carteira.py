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

# Teste api carteira

from fastapi.testclient import TestClient
from app.main import app
import tests.config as config

client = TestClient(app)

def test_cadastrar_carteira():
    pass

def test_atualizar_carteira():
    pass

def test_obter_carteira(): 
    response = client.get(f"/api/v1/carteiras/usuarios/{config.USUARIO_ID}", headers={'Authorization': f'Bearer {config.TOKEN}'} )
    assert response.status_code == 200 

def test_obter_carteiras(): 
    response = client.get(f"/api/v1/carteiras/{config.CARTEIRA_ID}/usuarios/{config.USUARIO_ID}", headers={'Authorization': f'Bearer {config.TOKEN}'} )
    assert response.status_code == 200 

def test_excluir_carteira(): 
    response = client.delete(f"/api/v1/carteiras/id", headers={'Authorization': f'Bearer {config.TOKEN}'} )
    assert response.status_code == 200     
    



 