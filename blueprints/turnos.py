import sqlite3
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_turno')
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_turno():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM turno ORDER BY nome')
            turnos = cursor.fetchall()
        return render_template('cadastro_turno.html', turnos=turnos)

    @app.route('/salvar_turno', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def salvar_turno():
        nome = request.form.get('nome', '').strip()

        if not nome:
            flash("O nome do turno é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_turno'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO turno (nome) VALUES (?)", (nome,))
                conexao.commit()
            return redirect(url_for('listar_turnos'))
        except sqlite3.IntegrityError:
            flash("Esse turno já está cadastrado.", 'erro')
            return redirect(url_for('cadastrar_turno'))

    @app.route('/turnos')
    @requer_perfil('diretor', 'secretaria')
    def listar_turnos():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM turno ORDER BY nome')
            turnos = cursor.fetchall()
        return render_template('turnos.html', turnos=turnos)

    @app.route('/editar_turno/<int:id_turno>')
    @requer_perfil('diretor', 'secretaria')
    def editar_turno(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM turno ORDER BY nome')
            turnos = cursor.fetchall()
            cursor.execute('SELECT * FROM turno WHERE id_turno = ?', (id_turno,))
            turno_edicao = cursor.fetchone()
        return render_template('turnos.html', turnos=turnos, turno_edicao=turno_edicao)

    @app.route('/atualizar_turno/<int:id_turno>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_turno(id_turno):
        nome = request.form.get('nome', '').strip()

        if not nome:
            flash("O nome do turno é obrigatório.", 'erro')
            return redirect(url_for('editar_turno', id_turno=id_turno))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE turno SET nome = ? WHERE id_turno = ?", (nome, id_turno))
            conexao.commit()
        return redirect(url_for('listar_turnos'))

    @app.route('/deletar_turno/<int:id_turno>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_turno(id_turno):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM turno WHERE id_turno = ?', (id_turno,))
            conexao.commit()
        return redirect(url_for('listar_turnos'))
