import unittest
from flask import Flask
from app import app, db  
from flask_testing import TestCase

class TestConfig(TestCase):
    """Configuração base para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  

    def create_app(self):
        app.config.from_object(self)  
        return app

    def setUp(self):
        """Função que será executada antes de cada teste."""
        db.create_all()  

    def tearDown(self):
        """Função que será executada após cada teste."""
        db.session.remove()
        db.drop_all()  

class TestRotas(TestConfig):
    """Teste das rotas da aplicação."""
    
    def test_home_page(self):
        """Testa se a página inicial carrega corretamente."""
        response = self.client.get('/')  # Simula um GET para a rota '/'
        self.assertEqual(response.status_code, 200)  # Verifica se o código de status é 200
        self.assertIn(b'Bem-vindo ao Inventário', response.data)  # Verifica se o texto está na resposta

    def test_listar_ativos(self):
        """Testa a rota de listar ativos."""
        response = self.client.get('/listar_ativos')  # Simula um GET para a rota de listar ativos
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lista de Ativos', response.data)

    def test_cadastro_ativos(self):
        """Testa a rota de cadastro de ativos."""
        response = self.client.post('/cadastro_ativos', data=dict(
            nome='Ativo Teste',
            descricao='Descrição Teste',
            patrimonio='12345'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ativo cadastrado com sucesso', response.data)

if __name__ == '__main__':
    unittest.main()