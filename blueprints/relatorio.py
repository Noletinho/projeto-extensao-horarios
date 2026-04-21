from db import conectar
from auth import requer_login, usuario_logado
from flask import render_template, Response, flash, redirect, url_for


def registrar(app):

    @app.route('/meu_horario')
    @requer_login
    def meu_horario():
        u = usuario_logado()
        if not u or u['perfil'] != 'professor' or not u['id_professor']:
            return redirect(url_for('index'))
        dados = _montar_dados_professor(u['id_professor'])
        return render_template('meu_horario.html', **dados)

    @app.route('/selecionar_turno_relatorio')
    @requer_login
    def selecionar_turno_relatorio():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('selecionar_turno_relatorio.html', turnos=turnos)

    @app.route('/relatorio_horario_turno/<int:id_turno>')
    @requer_login
    def relatorio_horario_turno(id_turno):
        turno, turmas, horarios, dias, grade = _montar_dados_relatorio(id_turno)
        if not turno:
            return redirect(url_for('selecionar_turno_relatorio'))
        if not turmas:
            flash('Este turno não possui turmas cadastradas.', 'erro')
            return redirect(url_for('selecionar_turno_relatorio'))
        return render_template('relatorio.html',
                               turno=turno, turmas=turmas,
                               horarios=horarios, dias=dias, grade=grade)

    @app.route('/baixar_relatorio_pdf/<int:id_turno>')
    @requer_login
    def baixar_relatorio_pdf(id_turno):
        flash("Para salvar em PDF: use o botão 'Imprimir / Salvar PDF' e escolha 'Salvar como PDF' no diálogo de impressão do navegador.", 'erro')
        return redirect(url_for('relatorio_horario_turno', id_turno=id_turno))


def _montar_dados_professor(id_professor):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM professor WHERE id_professor = %s", (id_professor,))
        row = cursor.fetchone()
        professor_nome = row['nome'] if row else 'Professor'
        cursor.execute("""
            SELECT * FROM horario_aula
            WHERE eh_intervalo = 1
               OR id_horario IN (
                   SELECT DISTINCT id_horario FROM alocacao WHERE id_professor = %s
               )
            ORDER BY hora_inicio
        """, (id_professor,))
        horarios = cursor.fetchall()
        cursor.execute("""
            SELECT a.dia_semana, a.id_horario,
                   d.nome AS nome_disciplina, d.sigla, d.cor,
                   t.nome AS nome_turma, t.serie,
                   l.nome AS nome_local
            FROM alocacao a
            JOIN disciplina d ON a.id_disciplina = d.id_disciplina
            JOIN turma t ON a.id_turma = t.id_turma
            JOIN `local` l ON a.id_local = l.id_local
            WHERE a.id_professor = %s
        """, (id_professor,))
        alocacoes = cursor.fetchall()
    dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
    grade = {}
    for a in alocacoes:
        ih  = a['id_horario']
        dia = a['dia_semana']
        if ih not in grade:
            grade[ih] = {}
        grade[ih][dia] = {
            'sigla':          a['sigla'],
            'cor':            a['cor'],
            'nome_disciplina': a['nome_disciplina'],
            'turma':          f"{a['nome_turma']} – {a['serie']}",
            'local':          a['nome_local'],
        }
    return {'professor_nome': professor_nome, 'horarios': horarios, 'dias': dias, 'grade': grade}


def _montar_dados_relatorio(id_turno):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
        turno = cursor.fetchone()
        if not turno:
            return None, None, None, None, None
        cursor.execute("""
            SELECT t.id_turma, t.nome, t.serie
            FROM turma t WHERE t.id_turno = %s
            ORDER BY t.serie, t.nome
        """, (id_turno,))
        turmas = cursor.fetchall()
        cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
        horarios = cursor.fetchall()
        cursor.execute("""
            SELECT a.id_turma, a.dia_semana, a.id_horario,
                   d.nome AS nome_disciplina, d.sigla, d.cor,
                   p.nome AS professor
            FROM alocacao a
            JOIN turma t ON a.id_turma = t.id_turma
            JOIN disciplina d ON a.id_disciplina = d.id_disciplina
            JOIN professor p ON a.id_professor = p.id_professor
            WHERE t.id_turno = %s
        """, (id_turno,))
        alocacoes = cursor.fetchall()

    dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']

    # Garante que o intervalo sempre aparece na 4ª posição (após 3 aulas)
    regulares = [h for h in horarios if not h['eh_intervalo']]
    intervalos = [h for h in horarios if h['eh_intervalo']]
    horarios = regulares[:3] + intervalos + regulares[3:]

    # Dicionário aninhado para evitar problemas de lookup com tupla no Jinja2
    grade = {}
    for a in alocacoes:
        ih  = a['id_horario']
        dia = a['dia_semana']
        it  = a['id_turma']
        if ih not in grade:
            grade[ih] = {}
        if dia not in grade[ih]:
            grade[ih][dia] = {}
        grade[ih][dia][it] = {
            'sigla':     a['sigla'],
            'cor':       a['cor'],
            'professor': a['professor'],
        }
    return turno, turmas, horarios, dias, grade
