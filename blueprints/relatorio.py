from db import conectar
from flask import render_template


def registrar(app):

    @app.route('/selecionar_turno_relatorio')
    def selecionar_turno_relatorio():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('selecionar_turno_relatorio.html', turnos=turnos)

    @app.route('/relatorio_horario_turno/<int:id_turno>')
    def relatorio_horario_turno(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno WHERE id_turno = ?", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno
                FROM turma t JOIN turno tr ON t.id_turno = tr.id_turno
                WHERE t.id_turno = ? ORDER BY t.nome
            """, (id_turno,))
            turmas = cursor.fetchall()
            cursor.execute("""
                SELECT id_horario, hora_inicio, hora_fim
                FROM horario_aula ORDER BY hora_inicio
            """)
            horarios = cursor.fetchall()
            cursor.execute("""
                SELECT a.dia_semana, a.id_turma, a.id_horario,
                       d.sigla, d.cor, p.nome AS nome_professor
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                WHERE t.id_turno = ?
                ORDER BY
                    CASE a.dia_semana
                        WHEN 'segunda' THEN 1 WHEN 'terca' THEN 2
                        WHEN 'quarta' THEN 3 WHEN 'quinta' THEN 4
                        WHEN 'sexta' THEN 5 END,
                    a.id_horario, a.id_turma
            """, (id_turno,))
            alocacoes = cursor.fetchall()

        dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
        grade = {}
        for a in alocacoes:
            grade[(a['id_horario'], a['dia_semana'], a['id_turma'])] = {
                'sigla': a['sigla'],
                'professor': a['nome_professor'],
                'cor': a['cor'] or '#ffffff'
            }

        return render_template('relatorio.html', dias=dias, turmas=turmas,
                               horarios=horarios, grade=grade, turno=turno)
