from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager 
from models.models import User, Ativo, Patrimonio
from forms.forms import LoginForm, CadastroAtivoForm, RegisterForm, CadastroPatrimonioForm, UploadFileForm
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError 
import os
import pandas as pd
from werkzeug.utils import secure_filename
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
    form.patrimonio_id.choices = [(p.id, p.placa_patrimonio) for p in Patrimonio.query.all()]
    if form.validate_on_submit():
        novo_ativo = Ativo(
            nome=form.nome.data,
            descricao=form.descricao.data,
            numero_serie=form.numero_serie.data,
            localizacao=form.localizacao.data,
            user_id=current_user.id,
            patrimonio_id=form.patrimonio_id.data
        )
        
        try:
            db.session.add(novo_ativo)
            db.session.commit()
            flash('Ativo cadastrado com sucesso!')
            return redirect(url_for('routes.listar_ativos'))
        except IntegrityError:
            db.session.rollback()  # Desfaz a transação
            flash('Erro: O número de série deve ser único. Já existe um ativo cadastrado com esse número de série.', 'danger')

    return render_template('cadastro_ativos.html', form=form)

@routes.route('/listar_ativos')
@login_required
def listar_ativos():
    page = request.args.get('page', 1, type=int)
    ativos = Ativo.query.paginate(page=page, per_page=15)
    return render_template('listar_ativos.html', ativos=ativos)


@routes.route('/cadastrar_patrimonio', methods=['GET', 'POST'])
@login_required  
def cadastrar_patrimonio():
    form = CadastroPatrimonioForm()
    if form.validate_on_submit():
        patrimonio = Patrimonio(
            placa_patrimonio=form.placa_patrimonio.data,
            codigo_compra=form.codigo_compra.data,
            cod_nfe=form.cod_nfe.data,
            usuario=form.usuario.data,
            fabricante=form.fabricante.data,
            processador=form.processador.data,
            modelo=form.modelo.data
        )
        db.session.add(patrimonio)
        db.session.commit()
        flash('Patrimônio cadastrado com sucesso!', 'success')
        return redirect(url_for('routes.listar_patrimonios'))
    return render_template('cadastrar_patrimonio.html', form=form)

@routes.route('/listar_patrimonios')
@login_required  
def listar_patrimonios():
    patrimonios = Patrimonio.query.all()
    return render_template('listar_patrimonios.html', patrimonios=patrimonios)

@routes.route('/editar_ativo/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_ativo(id):
    ativo = Ativo.query.get_or_404(id)
    form = CadastroAtivoForm(obj=ativo)

    if form.validate_on_submit():
        ativo.nome = form.nome.data
        ativo.descricao = form.descricao.data
        ativo.numero_serie = form.numero_serie.data
        ativo.localizacao = form.localizacao.data
        db.session.commit()
        flash('Ativo atualizado com sucesso!')
        return redirect(url_for('routes.listar_ativos'))

    return render_template('editar_ativo.html', form=form, ativo=ativo)

@routes.route('/excluir_ativo/<int:id>', methods=['POST'])
@login_required
def excluir_ativo(id):
    ativo = Ativo.query.get_or_404(id)
    db.session.delete(ativo)
    db.session.commit()
    flash('Ativo excluído com sucesso!')
    return redirect(url_for('routes.listar_ativos'))

@routes.route('/upload_excel', methods=['GET', 'POST'])
@login_required
def upload_excel():
    form = UploadFileForm()
    
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Salvar o arquivo no diretório especificado
        file.save(file_path)
        
        # Exibindo uma mensagem de sucesso após o upload
        flash('Arquivo Excel carregado com sucesso!', 'success')

    # Renderiza o template sem a variável df_filtered, já que não a está usando
    return render_template('upload_excel.html', form=form)
@routes.route('/exibir_dados', methods=['GET', 'POST'])
@login_required
def exibir_dados():
    planilhas_disponiveis = os.listdir(current_app.config['UPLOAD_FOLDER'])  
    df_filtered = None

    if request.method == 'POST':
        selected_file = request.form['planilha']
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], selected_file)

        if not os.path.exists(file_path):
            flash(f'O arquivo {selected_file} não foi encontrado.', 'danger')
            return render_template('exibir_dados.html', planilhas_disponiveis=planilhas_disponiveis, df_filtered=df_filtered)

        try:
            # Ler o arquivo Excel com header=0
            df_cleaned = pd.read_excel(file_path, header=0)  
            df_cleaned = df_cleaned.dropna(how='all', axis=1)  # Remove colunas vazias
            df_cleaned = df_cleaned.dropna(how='all')          # Remove linhas vazias

            # Verificar o número de colunas
            num_cols = len(df_cleaned.columns)
            
            # Definir os índices de colunas a serem mantidas, sem a coluna 'Dt. de Baixa'
            columns_to_keep = [
                0,  # 'Filial'
                1,  # 'Grupo'
                2,  # 'Classificac.'
                3,  # 'Cod. do Bem'
                4,  # 'Item'
                5,  # 'Dt. Aquisição'
                6,  # 'Quantidade'
                8,  # 'Descr. Sint.'
                9,  # 'Num. Placa'
                10, # 'Cod. Fornec.'
                11, # 'Loja Fornec.'
                12  # 'Nota Fiscal'
            ]

            # Garantir que os índices não excedam o número de colunas
            columns_to_keep = [i for i in columns_to_keep if i < num_cols]

            # Filtrar o DataFrame com as colunas selecionadas
            df_filtered = df_cleaned.iloc[:, columns_to_keep]
            
            # Renomeando as colunas conforme a ordem desejada
            df_filtered.columns = [
                'Filial', 
                'Grupo', 
                'Classificac.', 
                'Cod. do Bem', 
                'Item', 
                'Dt. Aquisição', 
                'Quantidade', 
                'Descr. Sint.', 
                'Num. Placa', 
                'Cod. Fornec.', 
                'Loja Fornec.', 
                'Nota Fiscal'
            ]
            
            # Converter a coluna 'Nota Fiscal' para inteiro
            df_filtered['Nota Fiscal'] = df_filtered['Nota Fiscal'].fillna(0).astype(int)
            df_filtered['Cod. Fornec.'] = df_filtered['Cod. Fornec.'].fillna(0).astype(int)
            df_filtered['Grupo'] = df_filtered['Grupo'].fillna(0).astype(int)
            df_filtered['Loja Fornec.'] = df_filtered['Loja Fornec.'].fillna(0).astype(int)
            df_filtered['Quantidade'] = df_filtered['Quantidade'].fillna(0).astype(int)

        except Exception as e:
            flash(f'Erro ao processar o arquivo: {str(e)}', 'danger')

    return render_template('exibir_dados.html', planilhas_disponiveis=planilhas_disponiveis, df_filtered=df_filtered)