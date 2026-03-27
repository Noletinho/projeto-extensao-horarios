import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def conectar():
    conexao = sqlite3.connect('escola_horarios.db')
    conexao.row_factory = sqlite3.Row
    return conexao

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/professores')
def listar_professores():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM professor')
    professores = cursor.fetchall()
    conexao.close()
    return render_template('professores.html', professores=professores)

@app.route('/cadastro_professor')
def cadastro_professor():
    return render_template('cadastro_professor.html')

@app.route('/salvar-professor', methods=['POST'])
def salvar_professor():
    nome = request.form['nome']
    cpf = request.form['cpf']
    email = request.form['email']
    telefone = request.form['telefone']

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    INSERT INTO professor (nome, cpf, email, telefone)
    VALUES (?, ?, ?, ?)
""", (nome, cpf, email, telefone))
    conexao.commit()
    conexao.close()

    return 'Professor salvo com sucesso!'

@app.route('/deletar_professor/<int:id_professor>', methods=['POST'])
def deletar_professor(id_professor):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM professor WHERE id_professor = ?', (id_professor,))
    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_professores'))

@app.route('/editar-professor/<int:id_professor>')
def editar_professor(id_professor):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM professor WHERE id_professor = ?', (id_professor,))
    professor = cursor.fetchone()
    conexao.close()

    return render_template('editar_professor.html', professor=professor)

@app.route('/atualizar-professor/<int:id_professor>', methods=['POST'])
def atualizar_professor(id_professor):
    nome = request.form['nome']
    cpf = request.form['cpf']
    email = request.form['email']
    telefone = request.form['telefone']
    status = request.form['status']

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE professor
        SET nome = ?, cpf = ?, email = ?, telefone = ?, status = ?
        WHERE id_professor = ?
    """, (nome, cpf, email, telefone, status, id_professor))
    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_professores'))

if __name__ == "__main__":
    app.run(debug=True)