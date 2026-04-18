import sqlite3
from db import conectar
from flask import render_template, request, redirect, url_for, flash


def registrar(app):

    @app.route('/cadastrar_turma')
    def cadastrar_turma():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_turno, nome FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
            cursor.execute("""
                SELECT turma.id_turma, turma.nome, turma.serie, turno.nome AS nome_turno
                FROM turma LEFT JOIN turno ON turma.id_turno = turno.id_turno
                ORDER BY turma.nome
            """)
            turmas = cursor.fetchall()
        return render_template('cadastro_turma.html', turnos=turnos, turmas=turmas)

    @app.route('/salvar_turma', methods=['POST'])
    def salvar_turma():
        nome = request.form.get('nome', '').strip()
        serie = request.form.get('serie', '').strip()
        id_turno = request.form.get('id_turno', '').strip()

        if not nome:
            flash("O nome da turma é obrigatório.", 'erro')
            return redirect(url_for('cadastrar_turma'))
        if not serie:
            flash("A série é obrigatória.", 'erro')
            return redirect(url_for('cadastrar_turma'))
        if not id_turno:
            flash("Selecione um turno.", 'erro')
            return redirect(url_for('cadastrar_turma'))

        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    INSERT INTO turma (nome, serie, id_turno)
                    VALUES (?, ?, ?)
                """, (nome, serie, id_turno))
                conexao.commit()
            return redirect(url_for('listar_turmas'))
        except sqlite3.IntegrityError:
            flash("Essa turma já existe.", 'erro')
            return redirect(url_for('cadastrar_turma'))

    @app.route('/turmas')
    def listar_turmas():
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT turma.id_turma, turma.nome, turma.serie, turma.id_turno,
                       turno.nome AS nome_turno
                FROM turma
                LEFT JOIN turno ON turma.id_turno = turno.id_turno
                ORDER BY turma.nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT id_turno, nome FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('turmas.html', turmas=turmas, turnos=turnos, turma_edicao=None)

    @app.route('/editar_turma/<int:id_turma>')
    def editar_turma(id_turma):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT turma.id_turma, turma.nome, turma.serie, turma.id_turno,
                       turno.nome AS nome_turno
                FROM turma
                JOIN turno ON turma.id_turno = turno.id_turno
                ORDER BY turma.nome
            """)
            turmas = cursor.fetchall()
            cursor.execute("SELECT * FROM turma WHERE id_turma = ?", (id_turma,))
            turma_edicao = cursor.fetchone()
            cursor.execute("SELECT id_turno, nome FROM turno ORDER BY nome")
            turnos = cursor.fetchall()
        return render_template('turmas.html', turmas=turmas, turnos=turnos, turma_edicao=turma_edicao)

    @app.route('/atualizar_turma/<int:id_turma>', methods=['POST'])
    def atualizar_turma(id_turma):
        nome = request.form.get('nome', '').strip()
        serie = request.form.get('serie', '').strip()
        id_turno = request.form.get('id_turno', '').strip()

        if not nome:
            flash("O nome da turma é obrigatório.", 'erro')
            return redirect(url_for('editar_turma', id_turma=id_turma))

        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE turma SET nome = ?, serie = ?, id_turno = ?
                WHERE id_turma = ?
            """, (nome, serie, id_turno, id_turma))
            conexao.commit()
        return redirect(url_for('listar_turmas'))

    @app.route('/deletar_turma/<int:id_turma>', methods=['POST'])
    def deletar_turma(id_turma):
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM turma WHERE id_turma = ?', (id_turma,))
            conexao.commit()
        return redirect(url_for('listar_turmas'))
