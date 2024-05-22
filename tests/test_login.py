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

# Teste api login

from fastapi.testclient import TestClient
from app.main import app
import tests.config as config 

client = TestClient(app)

def test_login_token(): 
    response = client.post("/api/v1/token", data={"username": config.USUARIO_EMAIL, "password": config.USUARIO_SENHA})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_token_sem_dados(): 
    response = client.post("/api/v1/token", data={"username": None, "password": None})
    assert response.status_code == 422 

def test_login_token_usuario_invalido(): 
    response = client.post("/api/v1/token", data={"username": config.USUARIO_EMAIL + "ERROR", "password": config.USUARIO_SENHA})
    assert response.status_code == 400

def test_login_token_senha_invalida(): 
    response = client.post("/api/v1/token", data={"username": config.USUARIO_EMAIL, "password": config.USUARIO_SENHA + "ERROR"})
    assert response.status_code == 400  

def test_trocar_senha(): 
    response = client.post("/api/v1/login/altera-senha/1", data={"email": config.USUARIO_EMAIL})
    assert response.status_code == 200

def test_trocar_senha_sem_email(): 
    response = client.post("/api/v1/login/altera-senha/1", data={"email": None})
    assert response.status_code == 422

def test_nova_senha(): 
    response = client.post("/api/v1/login/altera-senha/2", data={"token": config.TOKEN, "senha": config.USUARIO_SENHA})
    assert response.status_code == 200

def test_nova_senha_sem_senha(): 
    response = client.post("/api/v1/login/altera-senha/2", data={"token": config.TOKEN})
    assert response.status_code == 400