import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_alocacao', methods=['GET', 'POST'])
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_alocacao():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno
                FROM turma t JOIN turno tr ON t.id_turno = tr.id_turno ORDER BY t.nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT * FROM disciplina ORDER BY nome")
            disciplinas = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM `local` ORDER BY nome")
            locais = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()

            if request.method == 'POST':
                id_turma = request.form.get('id_turma', '').strip()
                id_disciplina = request.form.get('id_disciplina', '').strip()
                id_professor = request.form.get('id_professor', '').strip()
                id_local = request.form.get('id_local', '').strip()
                dia_semana = request.form.get('dia_semana', '').strip()
                ids_horarios = request.form.getlist('id_horarios')

                if not all([id_turma, id_disciplina, id_professor, id_local, dia_semana]) or not ids_horarios:
                    flash("Preencha todos os campos e selecione ao menos um horário.", 'erro')
                    return render_template('cadastro_alocacao.html', turmas=turmas,
                                           disciplinas=disciplinas, professores=professores,
                                           locais=locais, horarios=horarios)
                conflitos = 0
                inseridos = 0
                for id_horario in ids_horarios:
                    try:
                        cursor.execute("SAVEPOINT sp_alocacao")
                        cursor.execute("""
                            INSERT INTO alocacao
                                (id_turma, id_disciplina, id_professor, id_local, dia_semana, id_horario)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (id_turma, id_disciplina, id_professor, id_local, dia_semana, id_horario))
                        cursor.execute("RELEASE SAVEPOINT sp_alocacao")
                        inseridos += 1
                    except pymysql.IntegrityError:
                        cursor.execute("ROLLBACK TO SAVEPOINT sp_alocacao")
                        conflitos += 1
                conexao.commit()
                if conflitos:
                    flash(f"{conflitos} conflito(s) ignorado(s): professor, turma ou local já ocupado(s) no horário.", 'erro')
                if inseridos:
                    return redirect(url_for('selecionar_turno_alocacoes'))

        return render_template('cadastro_alocacao.html', turmas=turmas,
                               disciplinas=disciplinas, professores=professores,
                               locais=locais, horarios=horarios)

    @app.route('/selecionar_turno_alocacoes')
    @requer_perfil('diretor', 'secretaria')
    def selecionar_turno_alocacoes():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('selecionar_turno_alocacoes.html', turnos=turnos)

    @app.route('/alocacoes/<int:id_turno>')
    @requer_perfil('diretor', 'secretaria')
    def listar_alocacoes_turno(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT a.id_alocacao, a.id_turma, a.id_disciplina, a.id_professor,
                       a.id_local, a.dia_semana, a.id_horario,
                       t.nome AS nome_turma, t.serie,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       p.nome AS nome_professor,
                       l.nome AS nome_local,
                       h.hora_inicio, h.hora_fim
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                JOIN `local` l ON a.id_local = l.id_local
                JOIN horario_aula h ON a.id_horario = h.id_horario
                WHERE t.id_turno = %s
                ORDER BY t.serie, t.nome,
                    CASE a.dia_semana
                        WHEN 'segunda' THEN 1 WHEN 'terca' THEN 2
                        WHEN 'quarta' THEN 3 WHEN 'quinta' THEN 4
                        WHEN 'sexta' THEN 5 END,
                    h.hora_inicio
            """, (id_turno,))
            registros = cursor.fetchall()

        alocacoes_por_serie, ordem_series = _agregar_alocacoes(registros)
        return render_template('alocacao.html', turno=turno,
                               alocacoes_por_serie=alocacoes_por_serie,
                               ordem_series=ordem_series, alocacao_edicao=None)

    @app.route('/editar_alocacao/<int:id_alocacao>')
    @requer_perfil('diretor', 'secretaria')
    def editar_alocacao(id_alocacao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT a.*, t.id_turno FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma WHERE a.id_alocacao = %s
            """, (id_alocacao,))
            alocacao_edicao = cursor.fetchone()
            if not alocacao_edicao:
                return redirect(url_for('selecionar_turno_alocacoes'))

            id_turno = alocacao_edicao['id_turno']
            cursor.execute("SELECT * FROM turno WHERE id_turno = %s", (id_turno,))
            turno = cursor.fetchone()
            cursor.execute("""
                SELECT a.id_alocacao, a.id_turma, a.id_disciplina, a.id_professor,
                       a.id_local, a.dia_semana, a.id_horario,
                       t.nome AS nome_turma, t.serie,
                       d.nome AS nome_disciplina, d.sigla, d.cor,
                       p.nome AS nome_professor,
                       l.nome AS nome_local,
                       h.hora_inicio, h.hora_fim
                FROM alocacao a
                JOIN turma t ON a.id_turma = t.id_turma
                JOIN disciplina d ON a.id_disciplina = d.id_disciplina
                JOIN professor p ON a.id_professor = p.id_professor
                JOIN `local` l ON a.id_local = l.id_local
                JOIN horario_aula h ON a.id_horario = h.id_horario
                WHERE t.id_turno = %s
                ORDER BY t.serie, t.nome,
                    CASE a.dia_semana
                        WHEN 'segunda' THEN 1 WHEN 'terca' THEN 2
                        WHEN 'quarta' THEN 3 WHEN 'quinta' THEN 4
                        WHEN 'sexta' THEN 5 END,
                    h.hora_inicio
            """, (id_turno,))
            registros = cursor.fetchall()
            cursor.execute("""
                SELECT t.id_turma, t.nome, t.serie, tr.nome AS nome_turno
                FROM turma t JOIN turno tr ON t.id_turno = tr.id_turno ORDER BY t.nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT * FROM disciplina ORDER BY nome")
            disciplinas = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM `local` ORDER BY nome")
            locais = cursor.fetchall()
            cursor.execute("SELECT * FROM horario_aula ORDER BY hora_inicio")
            horarios = cursor.fetchall()

        alocacoes_por_serie, ordem_series = _agregar_alocacoes(registros)
        return render_template('alocacao.html', turno=turno,
                               alocacoes_por_serie=alocacoes_por_serie,
                               ordem_series=ordem_series, alocacao_edicao=alocacao_edicao,
                               turmas=turmas, disciplinas=disciplinas,
                               professores=professores, locais=locais, horarios=horarios)

    @app.route('/atualizar_alocacao/<int:id_alocacao>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_alocacao(id_alocacao):
        id_turma = request.form['id_turma']
        id_disciplina = request.form['id_disciplina']
        id_professor = request.form['id_professor']
        id_local = request.form['id_local']
        dia_semana = request.form['dia_semana']
        id_horario = request.form['id_horario']

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE alocacao
                    SET id_turma = %s, id_disciplina = %s, id_professor = %s,
                        id_local = %s, dia_semana = %s, id_horario = %s
                    WHERE id_alocacao = %s
                """, (id_turma, id_disciplina, id_professor, id_local,
                      dia_semana, id_horario, id_alocacao))
                conexao.commit()
            return redirect(url_for('selecionar_turno_alocacoes'))
        except pymysql.IntegrityError:
            flash("Conflito de horário: professor, turma ou local já está ocupado nesse dia e horário.",
                  'erro')
            return redirect(url_for('editar_alocacao', id_alocacao=id_alocacao))

    @app.route('/deletar_alocacao/<int:id_alocacao>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_alocacao(id_alocacao):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM alocacao WHERE id_alocacao = %s", (id_alocacao,))
            conexao.commit()
        return redirect(url_for('selecionar_turno_alocacoes'))


def _agregar_alocacoes(registros):
    alocacoes_por_serie = {}
    ordem_series = []
    for r in registros:
        serie = r['serie']
        id_turma = r['id_turma']
        if serie not in alocacoes_por_serie:
            alocacoes_por_serie[serie] = {}
            ordem_series.append(serie)
        if id_turma not in alocacoes_por_serie[serie]:
            alocacoes_por_serie[serie][id_turma] = {
                'id_turma': id_turma, 'nome_turma': r['nome_turma'], 'itens': []
            }
        alocacoes_por_serie[serie][id_turma]['itens'].append({
            'id_alocacao': r['id_alocacao'], 'dia_semana': r['dia_semana'],
            'hora_inicio': r['hora_inicio'], 'hora_fim': r['hora_fim'],
            'nome_disciplina': r['nome_disciplina'], 'sigla': r['sigla'],
            'cor': r['cor'], 'nome_professor': r['nome_professor'],
            'nome_local': r['nome_local']
        })
    return alocacoes_por_serie, ordem_series
