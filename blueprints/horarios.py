import sqlite3
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_horario')
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_horario():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM horario_aula ORDER BY hora_inicio')
            horarios = cursor.fetchall()
        return render_template('cadastro_horario.html', horarios=horarios)

    @app.route('/salvar_horario', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def salvar_horario():
        hora_inicio = request.form.get('hora_inicio', '').strip()
        hora_fim = request.form.get('hora_fim', '').strip()

        if not hora_inicio or not hora_fim:
            flash("Hora de início e hora de fim são obrigatórias.", 'erro')
            return redirect(url_for('cadastrar_horario'))

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
            flash("Esse horário já foi cadastrado.", 'erro')
            return redirect(url_for('cadastrar_horario'))

    @app.route('/horarios')
    @requer_perfil('diretor', 'secretaria')
    def listar_horarios():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM horario_aula ORDER BY hora_inicio')
            horarios = cursor.fetchall()
        return render_template('horarios_aula.html', horarios=horarios, horario_edicao=None)

    @app.route('/editar_horario/<int:id_horario>')
    @requer_perfil('diretor', 'secretaria')
    def editar_horario(id_horario):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM horario_aula ORDER BY hora_inicio')
            horarios = cursor.fetchall()
            cursor.execute('SELECT * FROM horario_aula WHERE id_horario = ?', (id_horario,))
            horario_edicao = cursor.fetchone()
        return render_template('horarios_aula.html', horarios=horarios, horario_edicao=horario_edicao)

    @app.route('/atualizar_horario/<int:id_horario>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_horario(id_horario):
        hora_inicio = request.form.get('hora_inicio', '').strip()
        hora_fim = request.form.get('hora_fim', '').strip()

        if not hora_inicio or not hora_fim:
            flash("Hora de início e hora de fim são obrigatórias.", 'erro')
            return redirect(url_for('editar_horario', id_horario=id_horario))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE horario_aula SET hora_inicio = ?, hora_fim = ?
                WHERE id_horario = ?
            """, (hora_inicio, hora_fim, id_horario))
            conexao.commit()
        return redirect(url_for('listar_horarios'))

    @app.route('/deletar_horario/<int:id_horario>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_horario(id_horario):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM horario_aula WHERE id_horario = ?', (id_horario,))
            conexao.commit()
        return redirect(url_for('listar_horarios'))
