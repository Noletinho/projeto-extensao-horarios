import sqlite3

comandos_sql = [
    """
    CREATE TABLE IF NOT EXISTS professor (
        id_professor INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE,
        email TEXT,
        telefone TEXT,
        status TEXT DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS turno (
        id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS turma (
        id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        serie TEXT NOT NULL,
        id_turno INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
        UNIQUE (nome, serie, id_turno)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS disciplina (
        id_disciplina INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        sigla TEXT NOT NULL UNIQUE,
        cor TEXT NOT NULL,
        carga_horaria_semanal INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS professor_disciplina (
        id_professor INTEGER NOT NULL,
        id_disciplina INTEGER NOT NULL,
        PRIMARY KEY (id_professor, id_disciplina),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
        FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS local (
        id_local INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL,
        status TEXT DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
        UNIQUE(nome)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS horario_aula (
        id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
        hora_inicio TEXT NOT NULL,
        hora_fim TEXT NOT NULL,
        UNIQUE(hora_inicio, hora_fim)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS disponibilidade_professor (
        id_disponibilidade INTEGER PRIMARY KEY AUTOINCREMENT,
        id_professor INTEGER NOT NULL,
        dia_semana TEXT NOT NULL CHECK (dia_semana IN ('segunda', 'terca', 'quarta', 'quinta', 'sexta')),
        id_horario INTEGER NOT NULL,
        disponivel INTEGER DEFAULT 1 CHECK (disponivel IN (0, 1)),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
        FOREIGN KEY (id_horario) REFERENCES horario_aula(id_horario),
        UNIQUE (id_professor, dia_semana, id_horario)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS grade_curricular (
        id_grade INTEGER PRIMARY KEY AUTOINCREMENT,
        id_turma INTEGER NOT NULL,
        id_disciplina INTEGER NOT NULL,
        aulas_semanais INTEGER NOT NULL,
        FOREIGN KEY (id_turma) REFERENCES turma(id_turma),
        FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina),
        UNIQUE (id_turma, id_disciplina)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS alocacao (
        id_alocacao INTEGER PRIMARY KEY AUTOINCREMENT,
        id_turma INTEGER NOT NULL,
        id_disciplina INTEGER NOT NULL,
        id_professor INTEGER NOT NULL,
        id_local INTEGER NOT NULL,
        dia_semana TEXT NOT NULL CHECK (dia_semana IN ('segunda', 'terca', 'quarta', 'quinta', 'sexta')),
        id_horario INTEGER NOT NULL,
        FOREIGN KEY (id_turma) REFERENCES turma(id_turma),
        FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina),
        FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
        FOREIGN KEY (id_local) REFERENCES local(id_local),
        FOREIGN KEY (id_horario) REFERENCES horario_aula(id_horario),
        UNIQUE (id_professor, dia_semana, id_horario),
        UNIQUE (id_turma, dia_semana, id_horario),
        UNIQUE (id_local, dia_semana, id_horario)
    )
    """
]

conexao = sqlite3.connect("escola_horarios.db")
cursor = conexao.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

for comando in comandos_sql:
    cursor.execute(comando)

conexao.commit()
conexao.close()

print("Banco SQLite criado com sucesso!")