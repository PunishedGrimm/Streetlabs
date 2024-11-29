import os
import logging
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal, InvalidOperation
from werkzeug.exceptions import RequestEntityTooLarge


app = Flask(__name__)

app.secret_key = os.urandom(24)

# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Endereço do MySQL no XAMPP
app.config['MYSQL_USER'] = 'root'       # Usuário padrão
app.config['MYSQL_PASSWORD'] = ''       # Senha (vazia por padrão)
app.config['MYSQL_DB'] = 'streetlabs'    # Nome do banco de dados

# Configuração de upload de arquivos
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


mysql = MySQL(app)

#link para outras paginas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/autenticacao', methods=['POST'])
def autenticacao():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM registro WHERE usuario = %s', (username,))
        user = cursor.fetchone()

        if user and user[4] == password:
            session['loggedin'] = True
            session['id'] = user[0]
            session['role'] = user[9]
            session['username'] = user[3]
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!', 'danger')
            return redirect(url_for('index'))

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
    role = "2"

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
        cursor.execute("INSERT INTO registro (nome, sobrenome, usuario, senha, email, endereco, role_user) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (nome, sobrenome, usuario, senha, email, endereco, role))
        mysql.connection.commit()
        cursor.close()
        return redirect('registro.html', mensagem="Cadastro realizado com sucesso!")
    except Exception as e:
        return f"Erro ao registrar: {str(e)}", 500
    
#Upload Produtos
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        categoria = request.form['categoria']
        tamanho = request.form['tamanho']
        tamanho_tenis = request.form['tamanho_tenis']
        cor = request.form['cor']
        estilo = request.form['estilo']
        
        # Upload da imagem
        if 'image' not in request.files:
            flash('Nenhuma imagem foi enviada!')
            return redirect(request.url)
        
        imagem = request.files['image']
        if imagem.filename == '':
            flash('Nenhuma imagem selecionada!')
            return redirect(request.url)
        
        if imagem:
            filename = secure_filename(imagem.filename)
            imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem.save(imagem_path)
            
            # Salvar no banco de dados
            try:
                cursor = mysql.connection.cursor()
                cursor.execute("""
                    INSERT INTO produtos 
                    (nome, descricao, preco, quantidade, categoria, tamanho, tamanho_tenis, cor, estilo, imagem) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, descricao, preco, quantidade, categoria, tamanho, tamanho_tenis, cor, estilo, filename))
                mysql.connection.commit()
                cursor.close()
                flash('Produto adicionado com sucesso!')
                return redirect('/adm')
            except Exception as e:
                flash(f'Erro ao adicionar produto: {str(e)}')
                return redirect(request.url)
    return render_template('admin.html')

#lista produtos
@app.route('/adm')
def admin_page():
    if 'role' not in session or session['role'] == 2:
        return redirect(url_for('index'))
    if session['role'] == 1:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM produtos")  # Certifique-se de que esta consulta está correta
        produtos = cursor.fetchall()  # Recupera todos os produtos do banco de dados
        cursor.close()

        # Imprima os produtos no console para verificar
        if not produtos:
            print("Nenhum produto encontrado.")
        else:
            print(f"Produtos recuperados: {produtos}")

        return render_template('admin.html', produtos=produtos)
    
@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi deslogado com sucesso.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
