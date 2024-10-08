from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='O nome de usuário é obrigatório.'), Length(min=4, max=150, message='O nome de usuário deve ter entre 4 e 150 caracteres.')])
    password = PasswordField('Password', validators=[DataRequired(message='A senha é obrigatória.')])
    submit = SubmitField('Login')

class CadastroAtivoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(message='O nome é obrigatório.')])
    descricao = StringField('Descrição', validators=[Optional(), Length(max=300, message='A descrição deve ter no máximo 300 caracteres.')])
    numero_serie = StringField('Número de Série', validators=[DataRequired(message='O número de série é obrigatório.')])
    localizacao = StringField('Localização', validators=[Optional(), Length(max=100, message='A localização deve ter no máximo 100 caracteres.')])
    patrimonio_id = SelectField('Patrimônio', choices=[], coerce=int, validators=[Optional()])
    submit = SubmitField('Cadastrar Ativo')

class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(message='O nome de usuário é obrigatório.')])
    password = PasswordField('Senha', validators=[DataRequired(message='A senha é obrigatória.')])
    confirm_password = PasswordField('Confirme a Senha', validators=[DataRequired(message='A confirmação da senha é obrigatória.'), EqualTo('password', message='As senhas devem corresponder.')])
    submit = SubmitField('Registrar')

class CadastroPatrimonioForm(FlaskForm):
    placa_patrimonio = StringField('Placa de Patrimônio', validators=[DataRequired(message='A placa de patrimônio é obrigatória.'), Length(max=50, message='A placa de patrimônio deve ter no máximo 50 caracteres.')])
    codigo_compra = StringField('Código de Compra', validators=[DataRequired(message='O código de compra é obrigatório.'), Length(max=50, message='O código de compra deve ter no máximo 50 caracteres.')])
    cod_nfe = StringField('Código da NFe', validators=[DataRequired(message='O código da NFe é obrigatório.'), Length(max=50, message='O código da NFe deve ter no máximo 50 caracteres.')])
    usuario = StringField('Usuário', validators=[DataRequired(message='O usuário é obrigatório.'), Length(max=150, message='O usuário deve ter no máximo 150 caracteres.')])
    fabricante = StringField('Fabricante', validators=[DataRequired(message='O fabricante é obrigatório.'), Length(max=100, message='O fabricante deve ter no máximo 100 caracteres.')])
    processador = StringField('Processador', validators=[DataRequired(message='O processador é obrigatório.'), Length(max=100, message='O processador deve ter no máximo 100 caracteres.')])
    modelo = StringField('Modelo', validators=[DataRequired(message='O modelo é obrigatório.'), Length(max=100, message='O modelo deve ter no máximo 100 caracteres.')])
    submit = SubmitField('Cadastrar Patrimônio')

class UploadFileForm(FlaskForm):
    file = FileField('Upload Excel', validators=[DataRequired()])
    submit = SubmitField('Upload')

class FilterForm(FlaskForm):
    filial = StringField('Filial', validators=[Optional()])
    grupo = IntegerField('Grupo', validators=[Optional()])
    classificacao = StringField('Classificação', validators=[Optional()])
    codigo_bem = StringField('Código do Bem', validators=[Optional()])
    nota_fiscal = IntegerField('Nota Fiscal', validators=[Optional()])
    descricao_sintetica = StringField('Descricao', validators=[Optional()])
    submit = SubmitField('Filtrar')

class AlterarStatusForm(FlaskForm):
    novo_status = SelectField('Novo Status', choices=[('Ativo', 'Ativo'), ('Inativo', 'Inativo'),('Ferias', 'Ferias')], default='', validators=[DataRequired()])
    submit = SubmitField('Alterar Status')