from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
