import sqlite3
from db import conectar
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# =========================
# PROFESSORES
# =========================


@app.route('/cadastrar_professor')
def cadastrar_professor():
    return render_template('cadastro_professor.html')


@app.route('/salvar_professor', methods=[ 'POST'])
def salvar_professor():
    erro = None
    
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = ''.join(filter(str.isdigit, request.form['cpf']))
        email = request.form['email']
        telefone = request.form['telefone']
        
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                INSERT INTO professor (nome, cpf, email, telefone)
                VALUES (?, ?, ?, ?)
                """, (nome, cpf, email, telefone))
                conexao.commit()

            return redirect(url_for('listar_professores'))
    
        except sqlite3.IntegrityError:
            erro = "CPF já cadastrado."

    return render_template('cadastro_professor.html', erro=erro)

@app.route('/professores')
def listar_professores():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM professor')
        professores = cursor.fetchall()

    return render_template('professores.html', professores=professores)

@app.route('/editar_professor/<int:id_professor>')
def editar_professor(id_professor):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM professor')
        professores = cursor.fetchall()

        cursor.execute('SELECT * FROM professor WHERE id_professor = ?', (id_professor,))
        professor_edicao = cursor.fetchone()


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

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE professor
            SET nome = ?, cpf = ?, email = ?, telefone = ?, status = ?
            WHERE id_professor = ?
        """, (nome, cpf, email, telefone, status, id_professor))
        conexao.commit()

    return redirect(url_for('listar_professores'))

@app.route('/deletar_professor/<int:id_professor>', methods=['POST'])
def deletar_professor(id_professor):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM professor WHERE id_professor = ?', (id_professor,))
        conexao.commit()

    return redirect(url_for('listar_professores'))


# =========================
# DISCIPLINAS
# =========================

@app.route('/cadastrar_disciplina')
def cadastrar_disciplina():
    return render_template('cadastro_disciplina.html')

@app.route('/salvar_disciplina', methods=['GET', 'POST'])
def salvar_disciplina():
    erro = None

    if request.method == 'POST':
        nome = request.form['nome']
        sigla = request.form['sigla']
        cor = request.form['cor']
        carga_horaria_semanal = request.form['carga_horaria_semanal']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                INSERT INTO disciplina (nome, sigla, cor, carga_horaria_semanal)
                VALUES (?, ?, ?, ?)
                """, (nome, sigla, cor, carga_horaria_semanal))    
                conexao.commit()

            return redirect(url_for('listar_disciplinas'))
        
        except sqlite3.IntegrityError:
            erro = "Já existe uma disciplina com esse nome ou sigla."

    return render_template('cadastro_disciplina.html', erro=erro)

@app.route('/disciplinas')
def listar_disciplinas():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM disciplina')
        disciplinas = cursor.fetchall()

    return render_template('disciplinas.html', disciplinas=disciplinas)

@app.route('/editar_disciplina/<int:id_disciplina>')
def editar_disciplina(id_disciplina):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM disciplina')
        disciplinas = cursor.fetchall()

        cursor.execute('SELECT * FROM disciplina WHERE id_disciplina = ?', (id_disciplina,))
        disciplina_edicao = cursor.fetchone()


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

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE disciplina
            SET nome = ?, sigla = ?, cor = ?, carga_horaria_semanal = ?
            WHERE id_disciplina = ?
        """, (nome, sigla, cor, carga_horaria_semanal, id_disciplina))
        conexao.commit()

    return redirect(url_for('listar_disciplinas'))
    
@app.route('/deletar-disciplina/<int:id_disciplina>', methods=['POST'])
def deletar_disciplina(id_disciplina):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM disciplina WHERE id_disciplina = ?', (id_disciplina,))
        conexao.commit()

    return redirect(url_for('listar_disciplinas'))


# =========================
# TURNOS
# =========================

@app.route('/cadastrar_turno')
def cadastrar_turno():
    return render_template('cadastro_turno.html')

@app.route('/salvar_turno', methods=['GET', 'POST'])
def salvar_turno():
    erro = None

    if request.method == 'POST':
        nome = request.form['nome']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                INSERT INTO turno (nome)
                VALUES (?) 
                """, (nome,))
                conexao.commit()

            return redirect(url_for('listar_turnos'))
        
        except sqlite3.IntegrityError:
            erro = "Esse turno já está cadastrado."

    return render_template('cadastro_turno.html', erro=erro)
    
@app.route('/turnos')
def listar_turnos():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM turno')
        turnos = cursor.fetchall()  

    return render_template('turnos.html', turnos=turnos)  

@app.route('/editar_turno/<int:id_turno>')
def editar_turno(id_turno):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM turno')
        turnos = cursor.fetchall()

        cursor.execute('SELECT * FROM turno WHERE id_turno = ?', (id_turno,))
        turno_edicao = cursor.fetchone()

    return render_template('turnos.html', turnos=turnos, turno_edicao=turno_edicao)

@app.route('/atualizar_turno/<int:id_turno>', methods=['POST'])
def atualizar_turno(id_turno):
    nome = request.form['nome']

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
        UPDATE turno
        SET nome = ?
        WHERE id_turno = ?
        """, (nome, id_turno))
        conexao.commit()

    return redirect(url_for('listar_turnos'))

@app.route('/deletar_turno/<int:id_turno>', methods=['POST'])
def deletar_turno(id_turno):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM turno WHERE id_turno = ?', (id_turno,))
        conexao.commit()

    return redirect(url_for('listar_turnos'))


# =========================
# Turmas
# =========================

@app.route('/cadastrar_turma')
def cadastrar_turma():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("SELECT id_turno, nome FROM turno")
        turnos = cursor.fetchall()

    return render_template('cadastro_turma.html', turnos=turnos)

@app.route('/salvar_turma', methods=['GET', 'POST'])
def salvar_turma():
    erro = None

    if request.method == 'POST':
        nome = request.form['nome']
        serie = request.form['serie']
        id_turno = request.form['id_turno']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                INSERT INTO turma (nome, serie, id_turno)
                VALUES(?, ?, ?)
                """,(nome, serie, id_turno))
                conexao.commit()

            return redirect(url_for('listar_turmas'))
        
        except sqlite3.IntegrityError:
            erro = "Essa turma já existe."

    return render_template('cadastro_turma.html', erro=erro)

@app.route('/turmas')
def listar_turmas():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT 
                turma.id_turma,
                turma.nome,
                turma.serie,
                turma.id_turno,
                turno.nome AS nome_turno
            FROM turma
            LEFT JOIN turno ON turma.id_turno = turno.id_turno
            ORDER BY turma.id_turma
        """)
        turmas = cursor.fetchall()

        cursor.execute("SELECT id_turno, nome FROM turno")
        turnos = cursor.fetchall()

    return render_template('turmas.html', turmas=turmas, turnos=turnos, turma_edicao=None)


@app.route('/editar_turma/<int:id_turma>')
def editar_turma(id_turma):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT 
                turma.id_turma,
                turma.nome,
                turma.serie,
                turma.id_turno,
                turno.nome AS nome_turno
            FROM turma
            JOIN turno ON turma.id_turno = turno.id_turno
        """)
        turmas = cursor.fetchall()

        cursor.execute("SELECT * FROM turma WHERE id_turma = ?", (id_turma,))
        turma_edicao = cursor.fetchone()

        cursor.execute("SELECT id_turno, nome FROM turno")
        turnos = cursor.fetchall()

    return render_template('turmas.html', turmas=turmas, turnos=turnos, turma_edicao=turma_edicao)

@app.route('/atualizar_turma/<int:id_turma>', methods=['POST'])
def atualizar_turma(id_turma):
    nome = request.form['nome']
    serie = request.form['serie']
    id_turno = request.form['id_turno']

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
        UPDATE turma
        SET nome = ?, serie = ?, id_turno = ?
        WHERE id_turma = ?
        """, (nome, serie, id_turno, id_turma))
        conexao.commit()
    
    return redirect(url_for('listar_turmas'))

@app.route('/deletar_turma/<int:id_turma>', methods=['POST'])
def deletar_turma(id_turma):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM turma WHERE id_turma = ?', (id_turma,))
        conexao.commit()

    return redirect(url_for('listar_turmas'))


# =========================
# Local
# =========================


@app.route('/cadastrar_local')
def cadastrar_local():
    return render_template('cadastro_local.html')


@app.route('/salvar_local', methods=['GET', 'POST'])
def salvar_local():
    erro = None

    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
    
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                    INSERT INTO local (nome, tipo)
                    VALUES (?, ?)
                """, (nome, tipo))
                conexao.commit()

            return redirect(url_for('listar_locais'))
        
        except sqlite3.IntegrityError:
            erro = "Já existe um local com esse nome."

    return render_template('cadastro_local.html', erro=erro)



@app.route('/locais')
def listar_locais():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM local")
        locais = cursor.fetchall()

    return render_template('locais.html', locais=locais, local_edicao=None)


@app.route('/editar_local/<int:id_local>')
def editar_local(id_local):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM local')
        locais = cursor.fetchall()

        cursor.execute('SELECT * FROM local WHERE id_local = ?', (id_local,))
        local_edicao = cursor.fetchone()

    return render_template('locais.html', locais=locais, local_edicao=local_edicao)

@app.route('/atualizar_local/<int:id_local>', methods=['POST'])
def atualizar_local(id_local):
    nome = request.form['nome']
    tipo = request.form['tipo']
    status = request.form['status']

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE local
            SET nome = ?, tipo = ?, status = ?
            WHERE id_local = ?
        """, (nome, tipo, status, id_local))
        conexao.commit()

    return redirect(url_for('listar_locais'))



@app.route('/deletar_local/<int:id_local>', methods=['POST'])
def deletar_local(id_local):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('DELETE FROM local WHERE id_local = ?', (id_local,))
        conexao.commit()

    return redirect(url_for('listar_locais'))


# =========================
# Horário Aula
# =========================

@app.route('/cadastrar_horario')
def cadastrar_horario():
    return render_template('cadastro_horario.html')

@app.route('/salvar_horario', methods=['GET', 'POST'])
def salvar_horario():
    erro = None

    if request.method == 'POST':
        hora_inicio = request.form['hora_inicio']
        hora_fim = request.form['hora_fim']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                    INSERT INTO horario_aula (hora_inicio, hora_fim)
                    VALUES (?, ?)
                """, (hora_inicio, hora_fim))
                conexao.commit()

            return redirect(url_for('listar_horarios'))
        
        except sqlite3.IntegrityError:
            erro = "Esse horário já foi cadastrado."

    return render_template('cadastro_horario.html', erro=erro)

@app.route('/horarios')
def listar_horarios():
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM horario_aula')
        horarios = cursor.fetchall()

    return render_template('horarios_aula.html', horarios=horarios, horario_edicao=None)

@app.route('/editar_horario/<int:id_horario>')
def editar_horario(id_horario):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM horario_aula')
        horario = cursor.fetchall()

        cursor.execute('SELECT * FROM horario_aula WHERE id_horario = ?', (id_horario,))
        horario_edicao = cursor.fetchone()

    return render_template('horarios_aula.html', horario=horario, horario_edicao=horario_edicao)

@app.route('/atualizar_horario/<int:id_horario>', methods=['POST'])
def atualizar_horario(id_horario):
    hora_inicio = request.form['hora_inicio']
    hora_fim = request.form['hora_fim']

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE horario_aula
            SET hora_inicio = ?, hora_fim = ?
            WHERE id_horario = ?
        """, (hora_inicio, hora_fim, id_horario))
        conexao.commit()

    return redirect(url_for('listar_horarios'))

@app.route('/deletar_horario/<int:id_horario>', methods=['POST'])
def deletar_horario(id_horario):
    with conectar() as conexao:
        cursor = conexao.cursor()
        
        cursor.execute('DELETE FROM horario_aula WHERE id_horario = ?', (id_horario,))
        conexao.commit()

    return redirect(url_for('listar_horarios'))


# =========================
# Professor - Disciplina
# =========================

@app.route('/cadastrar_professor_disciplina', methods=['GET', 'POST'])
def cadastrar_professor_disciplina():
    erro = None

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute('SELECT * FROM professor ORDER BY nome')
        professores = cursor.fetchall()

        cursor.execute('SELECT * FROM disciplina ORDER BY nome')
        disciplinas = cursor.fetchall()

        try:
            if request.method == 'POST':
                id_professor = request.form['id_professor']
                id_disciplina = request.form['id_disciplina']

                cursor.execute("""
                    INSERT INTO professor_disciplina (id_professor, id_disciplina)
                    VALUES (?, ?)
                """, (id_professor, id_disciplina))
                conexao.commit()

                return redirect(url_for('listar_professores_disciplinas'))
            
        except sqlite3.IntegrityError:
            erro = "Essa relação entre professor e disciplina já existe."

    return render_template(
        'cadastro_professor_disciplina.html', erro=erro,
        professores=professores, disciplinas=disciplinas)

@app.route('/professores_disciplinas')
def listar_professores_disciplinas():
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT 
                pd.id_professor,
                pd.id_disciplina,
                p.nome AS nome_professor,
                d.nome AS nome_disciplina,
                d.sigla
            FROM professor_disciplina pd
            JOIN professor p ON pd.id_professor = p.id_professor
            JOIN disciplina d ON pd.id_disciplina = d.id_disciplina
            ORDER BY p.nome, d.nome
        """)
        professores_disciplinas = cursor.fetchall()

    return render_template(
        'professor_disciplina.html',
        professores_disciplinas=professores_disciplinas,
        edicao_professor_disciplina=None)

@app.route('/editar_professor_disciplina/<int:id_professor>/<int:id_disciplina>')
def editar_professor_disciplina(id_professor, id_disciplina):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT 
                pd.id_professor,
                pd.id_disciplina,
                p.nome AS nome_professor,
                d.nome AS nome_disciplina,
                d.sigla
            FROM professor_disciplina pd
            JOIN professor p ON pd.id_professor = p.id_professor
            JOIN disciplina d ON pd.id_disciplina = d.id_disciplina
            ORDER BY p.nome, d.nome
        """)
        professores_disciplinas = cursor.fetchall()

        cursor.execute('SELECT * FROM professor ORDER BY nome')
        professores = cursor.fetchall()

        cursor.execute('SELECT * FROM disciplina ORDER BY nome')
        disciplinas = cursor.fetchall()

        cursor.execute("""
            SELECT * FROM professor_disciplina
            WHERE id_professor = ? AND id_disciplina = ?
        """,(id_professor, id_disciplina))
        professor_disciplina_edicao = cursor.fetchone()
    
    return render_template(
        'professor_disciplina.html',
        professores_disciplinas=professores_disciplinas,
        professor_disciplina_edicao=professor_disciplina_edicao,
        professores=professores,
        disciplinas=disciplinas)   

@app.route('/atualizar_professor_disciplina', methods=['POST'])
def atualizar_professor_disciplina():
    id_professor_antigo = request.form['id_professor_antigo']
    id_disciplina_antigo = request.form['id_disciplina_antiga']

    novo_id_professor = request.form['novo_id_professor']
    novo_id_disciplina = request.form['novo_id_disciplina']

    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE professor_disciplina
            SET id_professor = ?, id_disciplina = ?
            WHERE id_professor = ? AND id_disciplina = ?
        """, (
            novo_id_professor,
            novo_id_disciplina,
            id_professor_antigo,
            id_disciplina_antigo
        ))
        conexao.commit()

    return redirect(url_for('listar_professor_disciplina'))

@app.route('/deletar_professor_disciplina/<int:id_professor>/<int:id_disciplina>', methods=['POST'])
def deletar_professor_disciplina(id_professor, id_disciplina):
    with conectar() as conexao:
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM professor_disciplina
            WHERE id_professor = ? AND id_disciplina = ?
        """, (id_professor, id_disciplina))
        conexao.commit()

    return redirect(url_for('listar_professores_disciplinas'))


if __name__ == "__main__":
    app.run(debug=True)