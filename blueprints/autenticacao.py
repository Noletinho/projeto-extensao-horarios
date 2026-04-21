from db import conectar
from auth import requer_login
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash


def registrar(app):

    @app.route('/')
    @requer_login
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        from auth import usuario_logado
        if usuario_logado():
            return redirect(url_for('index'))
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            senha = request.form.get('senha', '')
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT * FROM usuario WHERE email = %s AND ativo = 1", (email,))
                usuario = cursor.fetchone()
            if usuario and check_password_hash(usuario['senha_hash'], senha):
                session.clear()
                session['usuario_id'] = usuario['id_usuario']
                session['usuario_nome'] = usuario['nome']
                session['usuario_perfil'] = usuario['perfil']
                session['usuario_id_professor'] = usuario['id_professor']
                session['usuario_primeiro_login'] = usuario['primeiro_login']
                if usuario['primeiro_login']:
                    flash("Bem-vindo! Por favor, altere sua senha antes de continuar.", 'erro')
                    return redirect(url_for('meu_perfil'))
                return redirect(url_for('index'))
            flash("E-mail ou senha inválidos.", 'erro')
        return render_template('login.html')

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/meu_perfil', methods=['GET', 'POST'])
    @requer_login
    def meu_perfil():
        from auth import usuario_logado
        u = usuario_logado()
        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip()
            senha_nova = request.form.get('senha_nova', '')
            senha_confirmar = request.form.get('senha_confirmar', '')

            if not nome or not email:
                flash("Nome e e-mail são obrigatórios.", 'erro')
                return redirect(url_for('meu_perfil'))
            if senha_nova and senha_nova != senha_confirmar:
                flash("As senhas não conferem.", 'erro')
                return redirect(url_for('meu_perfil'))

            with conectar() as conexao:
                cursor = conexao.cursor()
                if senha_nova:
                    cursor.execute("""
                        UPDATE usuario SET nome=%s, email=%s, senha_hash=%s, primeiro_login=0
                        WHERE id_usuario=%s
                    """, (nome, email, generate_password_hash(senha_nova), u['id']))
                else:
                    cursor.execute("""
                        UPDATE usuario SET nome=%s, email=%s WHERE id_usuario=%s
                    """, (nome, email, u['id']))
                conexao.commit()

            session['usuario_nome'] = nome
            session['usuario_primeiro_login'] = 0
            flash("Perfil atualizado com sucesso.", 'sucesso')
            return redirect(url_for('index'))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM usuario WHERE id_usuario=%s", (u['id'],))
            dados_usuario = cursor.fetchone()
        return render_template('meu_perfil.html', dados_usuario=dados_usuario)
