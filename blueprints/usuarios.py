import pymysql
from db import conectar
from auth import requer_perfil
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash


def registrar(app):

    @app.route('/usuarios')
    @requer_perfil('diretor')
    def listar_usuarios():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM usuario ORDER BY nome")
            usuarios = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
        return render_template('usuarios.html', usuarios=usuarios,
                               professores=professores, usuario_edicao=None)

    @app.route('/salvar_usuario', methods=['POST'])
    @requer_perfil('diretor')
    def salvar_usuario():
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        perfil = request.form.get('perfil', '').strip()
        id_professor = request.form.get('id_professor', '').strip() or None

        if not nome or not email or not senha or not perfil:
            flash("Preencha todos os campos obrigatórios.", 'erro')
            return redirect(url_for('listar_usuarios'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO usuario (nome, email, senha_hash, perfil, id_professor, primeiro_login)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """, (nome, email, generate_password_hash(senha), perfil, id_professor))
                conexao.commit()
            flash("Usuário cadastrado com sucesso.", 'sucesso')
            return redirect(url_for('listar_usuarios'))
        except pymysql.IntegrityError:
            flash("Já existe um usuário com esse e-mail.", 'erro')
            return redirect(url_for('listar_usuarios'))

    @app.route('/editar_usuario/<int:id_usuario>')
    @requer_perfil('diretor')
    def editar_usuario(id_usuario):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM usuario ORDER BY nome")
            usuarios = cursor.fetchall()
            cursor.execute("SELECT * FROM professor ORDER BY nome")
            professores = cursor.fetchall()
            cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
            usuario_edicao = cursor.fetchone()
        return render_template('usuarios.html', usuarios=usuarios,
                               professores=professores, usuario_edicao=usuario_edicao)

    @app.route('/atualizar_usuario/<int:id_usuario>', methods=['POST'])
    @requer_perfil('diretor')
    def atualizar_usuario(id_usuario):
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        perfil = request.form.get('perfil', '').strip()
        id_professor = request.form.get('id_professor', '').strip() or None

        if not nome or not email or not perfil:
            flash("Preencha todos os campos obrigatórios.", 'erro')
            return redirect(url_for('editar_usuario', id_usuario=id_usuario))

        with conectar() as conexao:
            cursor = conexao.cursor()
            if senha:
                cursor.execute("""
                    UPDATE usuario SET nome=%s, email=%s, senha_hash=%s, perfil=%s, id_professor=%s
                    WHERE id_usuario=%s
                """, (nome, email, generate_password_hash(senha), perfil, id_professor, id_usuario))
            else:
                cursor.execute("""
                    UPDATE usuario SET nome=%s, email=%s, perfil=%s, id_professor=%s
                    WHERE id_usuario=%s
                """, (nome, email, perfil, id_professor, id_usuario))
            conexao.commit()
        flash("Usuário atualizado.", 'sucesso')
        return redirect(url_for('listar_usuarios'))

    @app.route('/desativar_usuario/<int:id_usuario>', methods=['POST'])
    @requer_perfil('diretor')
    def desativar_usuario(id_usuario):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE usuario SET ativo=0 WHERE id_usuario=%s", (id_usuario,))
            conexao.commit()
        return redirect(url_for('listar_usuarios'))

    @app.route('/ativar_usuario/<int:id_usuario>', methods=['POST'])
    @requer_perfil('diretor')
    def ativar_usuario(id_usuario):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE usuario SET ativo=1 WHERE id_usuario=%s", (id_usuario,))
            conexao.commit()
        return redirect(url_for('listar_usuarios'))
