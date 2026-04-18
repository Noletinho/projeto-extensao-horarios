import sqlite3
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_professor')
    @requer_perfil('diretor', 'secretaria')
    def cadastrar_professor():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
        return render_template('cadastro_professor.html', professores=professores)

    @app.route('/salvar_professor', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def salvar_professor():
        nome = request.form.get('nome', '').strip()
        cpf = ''.join(filter(str.isdigit, request.form.get('cpf', '')))
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_professor'))
        if cpf and len(cpf) != 11:
            flash("O CPF deve ter exatamente 11 dígitos.", 'erro')
            return redirect(url_for('cadastrar_professor'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO professor (nome, cpf, email, telefone)
                    VALUES (?, ?, ?, ?)
                """, (nome, cpf or None, email, telefone))
                conexao.commit()
            return redirect(url_for('listar_professores'))
        except sqlite3.IntegrityError:
            flash("CPF já cadastrado.", 'erro')
            return redirect(url_for('cadastrar_professor'))

    @app.route('/professores')
    @requer_perfil('diretor', 'secretaria')
    def listar_professores():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
        return render_template('professores.html', professores=professores)

    @app.route('/editar_professor/<int:id_professor>')
    @requer_perfil('diretor', 'secretaria')
    def editar_professor(id_professor):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM professor ORDER BY nome')
            professores = cursor.fetchall()
            cursor.execute('SELECT * FROM professor WHERE id_professor = ?', (id_professor,))
            professor_edicao = cursor.fetchone()
        return render_template('professores.html', professores=professores, professor_edicao=professor_edicao)

    @app.route('/atualizar_professor/<int:id_professor>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def atualizar_professor(id_professor):
        nome = request.form.get('nome', '').strip()
        cpf = ''.join(filter(str.isdigit, request.form.get('cpf', '')))
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        status = request.form.get('status', 'ativo')

        if not nome:
            flash("O nome é obrigatório.", 'erro')
            return redirect(url_for('editar_professor', id_professor=id_professor))
        if cpf and len(cpf) != 11:
            flash("O CPF deve ter exatamente 11 dígitos.", 'erro')
            return redirect(url_for('editar_professor', id_professor=id_professor))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE professor
                SET nome = ?, cpf = ?, email = ?, telefone = ?, status = ?
                WHERE id_professor = ?
            """, (nome, cpf or None, email, telefone, status, id_professor))
            conexao.commit()
        return redirect(url_for('listar_professores'))

    @app.route('/deletar_professor/<int:id_professor>', methods=['POST'])
    @requer_perfil('diretor', 'secretaria')
    def deletar_professor(id_professor):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM professor WHERE id_professor = ?', (id_professor,))
            conexao.commit()
        return redirect(url_for('listar_professores'))
