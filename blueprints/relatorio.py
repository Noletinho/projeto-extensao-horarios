from db import conectar
from auth import requer_login
from flask import render_template


def registrar(app):

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
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno WHERE id_turno = ?", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie
                FROM turma t WHERE t.id_turno = ?
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
                WHERE t.id_turno = ?
            """, (id_turno,))
            alocacoes = cursor.fetchall()

        dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
        grade = {}
        for a in alocacoes:
            chave = (a['id_horario'], a['dia_semana'], a['id_turma'])
            grade[chave] = {
                'sigla': a['sigla'],
                'cor': a['cor'],
                'professor': a['professor'],
            }

        return render_template('relatorio.html',
                               turno=turno, turmas=turmas,
                               horarios=horarios, dias=dias, grade=grade)
