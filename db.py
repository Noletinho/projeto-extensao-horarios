import sqlite3

def conectar():
    conexao = sqlite3.connect('escola_horarios.db', timeout=10)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao
