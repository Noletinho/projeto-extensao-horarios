import sqlite3
from db import conectar
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_disciplina')
    def cadastrar_disciplina():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
        return render_template('cadastro_disciplina.html', disciplinas=disciplinas)

    @app.route('/salvar_disciplina', methods=['POST'])
    def salvar_disciplina():
        nome = request.form.get('nome', '').strip()
        sigla = request.form.get('sigla', '').strip()
        cor = request.form.get('cor', '#ffffff').strip()
        carga = request.form.get('carga_horaria_semanal', '').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))
        if not sigla:
            flash("A sigla é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))
        if not carga:
            flash("A carga horária é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO disciplina (nome, sigla, cor, carga_horaria_semanal)
                    VALUES (?, ?, ?, ?)
                """, (nome, sigla, cor, carga))
                conexao.commit()
            return redirect(url_for('listar_disciplinas'))
        except sqlite3.IntegrityError:
            flash("Já existe uma disciplina com esse nome ou sigla.", 'erro')
            return redirect(url_for('cadastrar_disciplina'))

    @app.route('/disciplinas')
    def listar_disciplinas():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
        return render_template('disciplinas.html', disciplinas=disciplinas)

    @app.route('/editar_disciplina/<int:id_disciplina>')
    def editar_disciplina(id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM disciplina ORDER BY nome')
            disciplinas = cursor.fetchall()
            cursor.execute('SELECT * FROM disciplina WHERE id_disciplina = ?', (id_disciplina,))
            disciplina_edicao = cursor.fetchone()
        return render_template('disciplinas.html', disciplinas=disciplinas, disciplina_edicao=disciplina_edicao)

    @app.route('/atualizar_disciplina/<int:id_disciplina>', methods=['POST'])
    def atualizar_disciplina(id_disciplina):
        nome = request.form.get('nome', '').strip()
        sigla = request.form.get('sigla', '').strip()
        cor = request.form.get('cor', '#ffffff').strip()
        carga = request.form.get('carga_horaria_semanal', '').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('editar_disciplina', id_disciplina=id_disciplina))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE disciplina
                SET nome = ?, sigla = ?, cor = ?, carga_horaria_semanal = ?
                WHERE id_disciplina = ?
            """, (nome, sigla, cor, carga, id_disciplina))
            conexao.commit()
        return redirect(url_for('listar_disciplinas'))

    @app.route('/deletar_disciplina/<int:id_disciplina>', methods=['POST'])
    def deletar_disciplina(id_disciplina):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM disciplina WHERE id_disciplina = ?', (id_disciplina,))
            conexao.commit()
        return redirect(url_for('listar_disciplinas'))
