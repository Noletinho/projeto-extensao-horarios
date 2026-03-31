from db import conectar
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# =========================
# PROFESSORES
# =========================


@app.route('/cadastro_professor')
def cadastro_professor():
    return render_template('cadastro_professor.html')


@app.route('/salvar_professor', methods=['POST'])
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

    return redirect(url_for('listar_professores'))

@app.route('/professores')
def listar_professores():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM professor')
    professores = cursor.fetchall()

    conexao.close()
    return render_template('professores.html', professores=professores)

@app.route('/editar_professor/<int:id_professor>')
def editar_professor(id_professor):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM professor')
    professores = cursor.fetchall()

    cursor.execute('SELECT * FROM professor WHERE id_professor = ?', (id_professor,))
    professor_edicao = cursor.fetchone()

    conexao.close()

    return render_template(
        'professores.html',
        professores=professores,
        professor_edicao=professor_edicao
    )

@app.route('/atualizar_professor/<int:id_professor>', methods=['POST'])
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

@app.route('/deletar_professor/<int:id_professor>', methods=['POST'])
def deletar_professor(id_professor):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM professor WHERE id_professor = ?', (id_professor,))

    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_professores'))


# =========================
# DISCIPLINAS
# =========================

@app.route('/cadastrar_disciplina')
def cadastrar_disciplina():
    return render_template('cadastro_disciplina.html')

@app.route('/salvar_disciplina', methods=['POST'])
def salvar_disciplina():
    nome = request.form['nome']
    sigla = request.form['sigla']
    cor = request.form['cor']
    carga_horaria_semanal = request.form['carga_horaria_semanal']

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO disciplina (nome, sigla, cor, carga_horaria_semanal)
    VALUES (?, ?, ?, ?)
""", (nome, sigla, cor, carga_horaria_semanal))
        
    conexao.commit()
    conexao.close()
    return redirect(url_for('listar_disciplinas'))

@app.route('/disciplinas')
def listar_disciplinas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM disciplina')
    disciplinas = cursor.fetchall()

    conexao.close()
    return render_template('disciplinas.html', disciplinas=disciplinas)

@app.route('/editar_disciplina/<int:id_disciplina>')
def editar_disciplina(id_disciplina):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM disciplina')
    disciplinas = cursor.fetchall()

    cursor.execute('SELECT * FROM disciplina WHERE id_disciplina = ?', (id_disciplina,))
    disciplina_edicao = cursor.fetchone()

    conexao.close()

    return render_template(
    'disciplinas.html',
    disciplinas=disciplinas,
    disciplina_edicao=disciplina_edicao
)

@app.route("/atualizar-disciplina/<int:id_disciplina>", methods=["POST"])
def atualizar_disciplina(id_disciplina):
    nome = request.form['nome']
    sigla = request.form['sigla']
    cor = request.form['cor']
    carga_horaria_semanal = request.form['carga_horaria_semanal']

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE disciplina
        SET nome = ?, sigla = ?, cor = ?, carga_horaria_semanal = ?
        WHERE id_disciplina = ?
    """, (nome, sigla, cor, carga_horaria_semanal, id_disciplina))

    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_disciplinas'))
    
@app.route('/deletar-disciplina/<int:id_disciplina>', methods=['POST'])
def deletar_disciplina(id_disciplina):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM disciplina WHERE id_disciplina = ?', (id_disciplina,))

    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_disciplinas'))


# =========================
# TURNOS
# =========================

@app.route('/cadastrar_turno')
def cadastrar_turno():
    return render_template('cadastro_turno.html')

@app.route('/salvar_turno', methods=['POST'])
def salvar_turno():
    nome = request.form['nome']

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    INSERT INTO turno (nome)
    VALUES (?) 
""", (nome,))
    
    conexao.commit()
    conexao.close()
    return redirect(url_for('listar_turnos'))
    
@app.route('/turnos')
def listar_turnos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM turno')
    turnos = cursor.fetchall()  

    conexao.close()
    return render_template('turnos.html', turnos=turnos)  

@app.route('/editar_turno/<int:id_turno>')
def editar_turno(id_turno):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM turno')
    turnos = cursor.fetchall()

    cursor.execute('SELECT * FROM turno WHERE id_turno = ?', (id_turno,))
    turno_edicao = cursor.fetchone()

    conexao.close()
    return render_template('turnos.html', turnos=turnos, turno_edicao=turno_edicao)

@app.route('/atualizar_turno/<int:id_turno>', methods=['POST'])
def atualizar_turno(id_turno):
    nome = request.form['nome']

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    UPDATE turno
    SET nome = ?
    WHERE id_turno = ?
""", (nome, id_turno))
    
    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_turnos'))

@app.route('/deletar_turno/<int:id_turno>', methods=['POST'])
def deletar_turno(id_turno):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('DELETE FROM turno WHERE id_turno = ?', (id_turno,))

    conexao.commit()
    conexao.close()

    return redirect(url_for('listar_turnos'))


# =========================
# Turmas
# =========================



if __name__ == "__main__":
    app.run(debug=True)