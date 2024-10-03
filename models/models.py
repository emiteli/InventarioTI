from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Ativo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.String(300))
    numero_serie = db.Column(db.String(100), nullable=False)
    localizacao = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Patrimonio(db.Model):
    __tablename__ = 'patrimonios'
    
    id = db.Column(db.Integer, primary_key=True)
    placa_patrimonio = db.Column(db.String(50), nullable=False)
    codigo_compra = db.Column(db.String(50), nullable=False)
    cod_nfe = db.Column(db.String(50), nullable=False)
    usuario = db.Column(db.String(150), nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    processador = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    

    def __repr__(self):
        return f'<Patrimonio {self.placa_patrimonio}>'