import sqlite3

def conectar():
    conexao = sqlite3.connect('escola_horarios.db')
    conexao.row_factory = sqlite3.Row
    return conexao