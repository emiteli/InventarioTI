from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager 
from models.models import User, Ativo, Patrimonio, Asset, Funcionario
from forms.forms import LoginForm, CadastroAtivoForm, RegisterForm, CadastroPatrimonioForm, UploadFileForm,  FilterForm, AlterarStatusForm
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError
import io
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
            db.session.rollback()
            flash('Erro: O número de série deve ser único. Já existe um ativo cadastrado com esse número de série.', 'danger')

    return render_template('cadastro_ativos.html', form=form)

@routes.route('/listar_ativos', methods=['GET', 'POST'])
@login_required
def listar_ativos():
    form = FilterForm()

    # Consulta inicial, sem filtros
    query = Asset.query

    # Aplicar os filtros baseados nos campos do formulário
    if form.validate_on_submit():
        if form.filial.data:
            query = query.filter(Asset.filial.ilike(f'%{form.filial.data}%'))
        if form.grupo.data:
            query = query.filter_by(grupo=form.grupo.data)
        if form.classificacao.data:
            query = query.filter(Asset.classificacao.ilike(f'%{form.classificacao.data}%'))
        if form.descricao_sintetica.data:
            query = query.filter(Asset.descricao_sintetica.ilike(f'%{form.descricao_sintetica.data}%'))
        if form.codigo_bem.data:
            query = query.filter(Asset.codigo_bem.ilike(f'%{form.codigo_bem.data}%'))
        if form.nota_fiscal.data:
            query = query.filter_by(nota_fiscal=form.nota_fiscal.data)

    # Executar a consulta
    ativos = query.all()
    return render_template('listar_ativos.html', form=form, ativos=ativos)



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
        
        file.save(file_path)

        flash('Arquivo Excel carregado com sucesso!', 'success')
    return render_template('upload_excel.html', form=form)

@routes.route('/exibir_dados', methods=['GET', 'POST'])
@login_required
def exibir_dados():
    planilhas_disponiveis = os.listdir(current_app.config['UPLOAD_FOLDER'])  
    df_filtered = None

    if request.method == 'POST':
        selected_file = request.form['planilha']
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], selected_file)
        tipo_banco = request.form['tipo_banco']

        if not os.path.exists(file_path):
            flash(f'O arquivo {selected_file} não foi encontrado.', 'danger')
            return render_template('exibir_dados.html', planilhas_disponiveis=planilhas_disponiveis, df_filtered=df_filtered)

        try:
            # Lê a planilha, mantendo todos os dados
            df_cleaned = pd.read_excel(file_path, header=0)  

            # Remover apenas colunas completamente vazias
            df_cleaned = df_cleaned.dropna(how='all', axis=1)

            # Preencher valores NaN com None para tratamento posterior no banco de dados
            df_cleaned = df_cleaned.where(df_cleaned.notnull(), None)

            # Define as colunas que você deseja manter
            if tipo_banco == 'asset':
                df_filtered = df_cleaned.iloc[:, [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12]]
                df_filtered.columns = ['Filial', 'Grupo', 'Classificac.', 'Cod. do Bem', 'Item', 'Dt. Aquisição', 'Quantidade', 'Descr. Sint.', 'Num. Placa', 'Cod. Fornec.', 'Loja Fornec.', 'Nota Fiscal']

                for index, row in df_filtered.iterrows():
                    existing_asset = Asset.query.filter_by(codigo_bem=row['Cod. do Bem']).first()

                    if not existing_asset:
                        new_asset = Asset(
                            filial=row['Filial'],
                            grupo=row['Grupo'],
                            classificacao=row['Classificac.'],
                            codigo_bem=row['Cod. do Bem'],
                            item=row['Item'],
                            data_aquisicao=pd.to_datetime(row['Dt. Aquisição'], errors='coerce').date() if row['Dt. Aquisição'] else None,
                            quantidade=row['Quantidade'],
                            descricao_sintetica=row['Descr. Sint.'],
                            numero_placa=row['Num. Placa'],
                            codigo_fornecedor=row['Cod. Fornec.'],
                            loja_fornecedor=row['Loja Fornec.'],
                            nota_fiscal=row['Nota Fiscal']
                        )
                        db.session.add(new_asset)

            elif tipo_banco == 'funcionario':
                df_filtered = df_cleaned.iloc[:, [0, 1, 2, 3, 4, 5]]
                df_filtered.columns = ['STATUS', 'DEPARTAMENTO', 'NOME', 'LICENCAS', 'CARGO', 'EMAIL']

                for index, row in df_filtered.iterrows():
                    # Verifique se as colunas obrigatórias não estão vazias
                    if not row['DEPARTAMENTO'] and not row['NOME'] and not row['EMAIL']:
                        # Se todos os campos estiverem vazios, continue para a próxima linha
                        continue  # Ignore essa linha e passe para a próxima

                    existing_funcionario = Funcionario.query.filter_by(email=row['EMAIL']).first()

                    if not existing_funcionario:
                        new_funcionario = Funcionario(
                            status=row['STATUS'] if row['STATUS'] else None,
                            departamento=row['DEPARTAMENTO'] if row['DEPARTAMENTO'] else None,
                            nome=row['NOME'] if row['NOME'] else None,
                            licencas=row['LICENCAS'] if row['LICENCAS'] else None,
                            cargo=row['CARGO'] if row['CARGO'] else None,
                            email=row['EMAIL'] if row['EMAIL'] else None
                        )
                        db.session.add(new_funcionario)

            db.session.commit()
            flash('Dados foram inseridos com sucesso no banco de dados.', 'success')

        except Exception as e:
            db.session.rollback()  # Faça rollback em caso de erro
            flash(f'Erro ao processar o arquivo: {str(e)}', 'danger')

    return render_template('exibir_dados.html', planilhas_disponiveis=planilhas_disponiveis, df_filtered=df_filtered)

@routes.route('/listar_funcionarios', methods=['GET', 'POST'])
@login_required
def listar_funcionarios():
    form = AlterarStatusForm()  # Instancia o formulário
    
    if request.method == 'POST' and form.validate_on_submit():
        funcionario_id = request.form.get('funcionario_id')
        novo_status = form.novo_status.data
        funcionario = Funcionario.query.get(funcionario_id)

        if funcionario:
            funcionario.status = novo_status
            db.session.commit()
            flash('Status alterado com sucesso!', 'success')
        else:
            flash('Funcionário não encontrado.', 'danger')

    funcionarios = Funcionario.query.all()  # Recupera todos os funcionários
    return render_template('listar_funcionarios.html', funcionarios=funcionarios, form=form)

@routes.route('/alterar_status/<int:funcionario_id>', methods=['POST'])
@login_required
def alterar_status(funcionario_id):
    form = AlterarStatusForm()

    if form.validate_on_submit():  # Valida o formulário
        novo_status = form.novo_status.data  # Pega o novo status do formulário
        funcionario = Funcionario.query.get(funcionario_id)  # Busca o funcionário pelo ID

        if funcionario:
            funcionario.status = novo_status  # Altera o status
            try:
                db.session.commit()  # Salva no banco de dados
                flash('Status alterado com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()  # Rollback em caso de erro
                flash(f'Erro ao salvar no banco: {str(e)}', 'danger')
        else:
            flash('Funcionário não encontrado.', 'danger')

    return redirect(url_for('routes.listar_funcionarios'))  # Redireciona para a lista de funcionários

@routes.route('/exportar_funcionarios', methods=['GET'])
@login_required
def exportar_funcionarios():
    funcionarios = Funcionario.query.all()  # Recupera todos os funcionários do banco de dados

    # Converte os dados para um DataFrame do pandas
    data = {
        'Status': [funcionario.status for funcionario in funcionarios],
        'Departamento': [funcionario.departamento for funcionario in funcionarios],
        'Nome': [funcionario.nome for funcionario in funcionarios],
        'Licenças': [funcionario.licencas for funcionario in funcionarios],
        'Cargo': [funcionario.cargo for funcionario in funcionarios],
        'Email': [funcionario.email for funcionario in funcionarios]
    }
    df = pd.DataFrame(data)

    # Salva o DataFrame em um objeto BytesIO (em memória)
    output = io.BytesIO()
    
    # Escreve o DataFrame em um arquivo Excel dentro do objeto BytesIO
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Funcionarios')
    
    output.seek(0)  # Move o ponteiro para o início do arquivo em memória

    # Envia o arquivo Excel para download
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     as_attachment=True, download_name='funcionarios_exportados.xlsx')
