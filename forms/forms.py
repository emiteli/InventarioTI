from flask_wtf import FlaskForm
from wtforms import  PasswordField,StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CadastroAtivoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = StringField('Descrição')
    numero_serie = StringField('Número de Série', validators=[DataRequired()])
    localizacao = StringField('Localização')
    submit = SubmitField('Cadastrar Ativo')

class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

class CadastroPatrimonioForm(FlaskForm):
    placa_patrimonio = StringField('Placa de Patrimônio', validators=[DataRequired(), Length(max=50)])
    codigo_compra = StringField('Código de Compra', validators=[DataRequired(), Length(max=50)])
    cod_nfe = StringField('Código da NFe', validators=[DataRequired(), Length(max=50)])
    usuario = StringField('Usuário', validators=[DataRequired(), Length(max=150)])
    fabricante = StringField('Fabricante', validators=[DataRequired(), Length(max=100)])
    processador = StringField('Processador', validators=[DataRequired(), Length(max=100)])
    modelo = StringField('Modelo', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Cadastrar Patrimônio')