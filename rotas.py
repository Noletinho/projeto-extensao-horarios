from flask import Flask
import auth

from blueprints import (
    autenticacao, professores, disciplinas, turnos, turmas, locais,
    horarios, professor_disciplina, disponibilidade,
    grade_curricular, alocacao, relatorio, usuarios
)

app = Flask(__name__)
app.secret_key = 'escola_horarios_chave_secreta_2024'

autenticacao.registrar(app)
professores.registrar(app)
disciplinas.registrar(app)
turnos.registrar(app)
turmas.registrar(app)
locais.registrar(app)
horarios.registrar(app)
professor_disciplina.registrar(app)
disponibilidade.registrar(app)
grade_curricular.registrar(app)
alocacao.registrar(app)
relatorio.registrar(app)
usuarios.registrar(app)


@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())


if __name__ == "__main__":
    app.run(debug=True)
