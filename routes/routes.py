from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from extensions import db, login_manager 
from models.models import User, Ativo, Fornecedor
from forms.forms import LoginForm, CadastroAtivoForm, RegisterForm
from flask_login import current_user

routes = Blueprint('routes', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@routes.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('routes.listar_ativos'))
    return redirect(url_for('routes.login'))


@routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Nome de usuário já está em uso!', 'danger')
            return redirect(url_for('routes.register'))
        
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Cadastro realizado com sucesso. Agora você pode fazer login!', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):  
            login_user(user)
            return redirect(url_for('routes.listar_ativos'))
        else:
            flash('Login inválido!')
    return render_template('login.html', form=form)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@routes.route('/cadastro_ativos', methods=['GET', 'POST'])
@login_required
def cadastro_ativos():
    form = CadastroAtivoForm()
    if form.validate_on_submit():
        novo_ativo = Ativo(
            nome=form.nome.data,
            descricao=form.descricao.data,
            numero_serie=form.numero_serie.data,
            localizacao=form.localizacao.data
        )
        db.session.add(novo_ativo)
        db.session.commit()
        flash('Ativo cadastrado com sucesso!')
        return redirect(url_for('routes.listar_ativos'))
    return render_template('cadastro_ativos.html', form=form)

@routes.route('/listar_ativos')
@login_required
def listar_ativos():
    page = request.args.get('page', 1, type=int)
    ativos = Ativo.query.paginate(page=page, per_page=15)
    return render_template('listar_ativos.html', ativos=ativos)

@routes.route('/listar_fornecedores')
@login_required
def listar_fornecedores():
    fornecedores = Fornecedor.query.all()
    return render_template('fornecedor/listar_fornecedores.html', fornecedores=fornecedores)