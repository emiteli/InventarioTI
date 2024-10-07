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
    numero_serie = db.Column(db.String(100), nullable=False, unique=True)
    localizacao = db.Column(db.String(100), nullable=False)
    filial = db.Column(db.String(50), nullable=True)
    cod_base_bem = db.Column(db.String(50), nullable=True)
    codigo_item = db.Column(db.String(50), nullable=True)
    tipo_ativo = db.Column(db.String(50), nullable=True)
    historico = db.Column(db.String(300), nullable=True)
    conta = db.Column(db.String(50), nullable=True)
    tipo_deprec = db.Column(db.String(50), nullable=True)
    ativo_origem = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patrimonio_id = db.Column(db.Integer, db.ForeignKey('patrimonios.id'), nullable=True)
    patrimonio = db.relationship('Patrimonio', backref='ativo')

class Patrimonio(db.Model):
    __tablename__ = 'patrimonios'
    
    id = db.Column(db.Integer, primary_key=True)
    placa_patrimonio = db.Column(db.String(50), nullable=False, unique=True)
    codigo_compra = db.Column(db.String(50), nullable=False)
    cod_nfe = db.Column(db.String(50), nullable=False)
    usuario = db.Column(db.String(150), nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    processador = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Patrimonio {self.placa_patrimonio}>'