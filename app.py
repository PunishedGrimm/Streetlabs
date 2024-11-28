import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal, InvalidOperation
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

app.secret_key = os.urandom(24)

# Configurações de segurança e upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Endereço do MySQL no XAMPP
app.config['MYSQL_USER'] = 'root'       # Usuário padrão
app.config['MYSQL_PASSWORD'] = ''       # Senha (vazia por padrão)
app.config['MYSQL_DB'] = 'streetlabs'    # Nome do banco de dados

mysql = MySQL(app)

#link para outras paginas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')
    
@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/procura')
def procura():
    return render_template('procura.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/meuspedidos')
def meuspedidos():
    return render_template('meuspedidos.html')

@app.route('/favorito')
def favorito():
    return render_template('favorite.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/adm')
def admin():
    return render_template('admin.html')

#registro de usuário
@app.route('/registro', methods=['POST'])
def add_user():
    nome = request.form.get('nome')
    sobrenome = request.form.get('sobrenome')
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    conf_senha = request.form.get('conf_senha')
    email = request.form.get('email')
    conf_email = request.form.get('conf_email')
    endereco = request.form.get('endereco')
    termos = request.form.get('termos')

    # Validações
    if not nome or not sobrenome or not usuario or not senha or not conf_senha or not email or not conf_email or not endereco:
        return "Por favor, preencha todos os campos!", 400

    if senha != conf_senha:
        return "As senhas não coincidem!", 400

    if email != conf_email:
        return "Os e-mails não coincidem!", 400

    if not termos:
        return "Você deve aceitar os termos para se cadastrar!", 400

    # Inserção no banco de dados
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO registro (nome, sobrenome, usuario, senha, email, endereco) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (nome, sobrenome, usuario, senha, email, endereco))
        mysql.connection.commit()
        cursor.close()
        return render_template('registro.html', mensagem="Cadastro realizado com sucesso!")
    except Exception as e:
        return f"Erro ao registrar: {str(e)}", 500
    
#Upload de Produtos
# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funções auxiliares
def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validar_dados_produto(dados):
    """
    Valida os dados do produto antes de inserir no banco de dados.
    Retorna uma lista de erros, se houver.
    """
    erros = []

    # Validação de nome
    if not dados['nome'] or len(dados['nome']) < 2:
        erros.append("Nome do produto deve ter pelo menos 2 caracteres")

    # Validação de descrição
    if not dados['descricao']:
        erros.append("Descrição do produto é obrigatória")

    # Validação de preço
    try:
        preco = Decimal(dados['preco'].replace(',', '.'))
        if preco <= 0:
            erros.append("Preço deve ser maior que zero")
    except (InvalidOperation, ValueError):
        erros.append("Preço inválido")

    # Validação de quantidade
    try:
        quantidade = int(dados['quantidade'])
        if quantidade < 0:
            erros.append("Quantidade não pode ser negativa")
    except ValueError:
        erros.append("Quantidade inválida")

    # Validação de categoria
    categorias_validas = [
        'camisas', 'blusas', 'saias_minissaia', 'calcas', 'tenis', 
        'jaqueta', 'macacao', 'bone', 'sandalias', 'cargo_pants', 
        'joggers', 'shorts', 'sueter', 'pijama', 'long_sleeve'
    ]
    if dados['categoria'] not in categorias_validas:
        erros.append("Categoria inválida")

    return erros

@app.route('/adicionar', methods=['POST'])
def adicionar_produto():
    try:
        # Criar pasta de uploads se não existir
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Captura dados do formulário
        dados_produto = {
            'nome': request.form.get('nome', '').strip(),
            'descricao': request.form.get('descricao', '').strip(),
            'preco': request.form.get('preco', '0').strip(),
            'quantidade': request.form.get('quantidade', '0').strip(),
            'categoria': request.form.get('categoria', ''),
            'tamanho': request.form.get('tamanho', '').strip(),
            'tamanho_tenis': request.form.get('tamanho_tenis', '').strip(),
            'cor': request.form.get('cor', '').strip(),
            'estilo': request.form.get('estilo', '').strip()
        }

        # Validação dos dados
        erros_validacao = validar_dados_produto(dados_produto)
        if erros_validacao:
            for erro in erros_validacao:
                flash(erro, 'danger')
            return redirect('/adm')
        

        # Tratamento de imagem
        imagem_path = app.config['UPLOAD_FOLDER'] = 'static/uploads'
        if 'image' in request.files:
            imagem = request.files['image']
            if imagem and imagem.filename != '':
                if allowed_file(imagem.filename):
                    filename = secure_filename(imagem.filename)
                    imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    imagem.save(imagem_path)
                    # Salva apenas o nome do arquivo no banco
                    imagem_path = filename
                else:
                    flash('Tipo de arquivo de imagem não permitido', 'danger')
                    return redirect('/adm')

        # Preparar dados para inserção
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO produtos 
            (nome, descricao, preco, quantidade, categoria, tamanho, 
            tamanho_tenis, cor, estilo, imagem) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            dados_produto['nome'], 
            dados_produto['descricao'], 
            Decimal(dados_produto['preco'].replace(',', '.')), 
            int(dados_produto['quantidade']), 
            dados_produto['categoria'], 
            dados_produto['tamanho'], 
            dados_produto['tamanho_tenis'], 
            dados_produto['cor'], 
            dados_produto['estilo'], 
            imagem_path
        ))

        mysql.connection.commit()
        cursor.close()

        # Log de sucesso
        logger.info(f"Produto {dados_produto['nome']} adicionado com sucesso")
        flash('Produto adicionado com sucesso!', 'success')
        return redirect('/adm')

    except RequestEntityTooLarge:
        flash('Arquivo de imagem muito grande. Limite máximo: 16MB', 'danger')
        return redirect('/adm')
    except Exception as e:
        # Log do erro para depuração
        logger.error(f"Erro ao adicionar produto: {e}", exc_info=True)
        flash(f'Erro ao adicionar produto: {str(e)}', 'danger')
        mysql.connection.rollback()
        return redirect('/adm')


if __name__ == '__main__':
    app.run(debug=True)
