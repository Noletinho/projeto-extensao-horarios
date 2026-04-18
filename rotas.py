from flask import Flask, render_template

from blueprints import (
    professores, disciplinas, turnos, turmas, locais,
    horarios, professor_disciplina, disponibilidade,
    grade_curricular, alocacao, relatorio
)

app = Flask(__name__)
app.secret_key = 'escola_horarios_chave_secreta_2024'

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


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
