# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos Essenciais

```bash
# Inicializar o banco de dados (apenas uma vez ou para recriar)
python criar_banco.py

# Executar a aplicação
python rotas.py
# Acesso em: http://127.0.0.1:5000

# Instalar dependências
pip install -r requirements.txt
```

## Arquitetura

Sistema de gerenciamento de horários escolares — Flask monolítico com renderização server-side via Jinja2 e banco SQLite.

### Camadas

| Arquivo/Pasta | Responsabilidade |
|---------------|-----------------|
| `rotas.py` | Ponto de entrada: cria o app Flask, registra todos os módulos de rotas e define a rota raiz `/` |
| `blueprints/` | Um módulo por entidade; cada módulo exporta `registrar(app)` que define as rotas diretamente no app |
| `db.py` | Único utilitário: `conectar()` retorna conexão SQLite com `row_factory = sqlite3.Row` e `PRAGMA foreign_keys = ON` |
| `criar_banco.py` | Script de criação do schema (executar uma vez) |
| `templates/` | Templates Jinja2; todos herdam de `base.html` exceto `relatorio.html` (layout de impressão) |
| `static/css/style.css` | Folha de estilos global com variáveis CSS e componentes |
| `escola_horarios.db` | Banco SQLite (ignorado no git) |

### Módulos de Rotas (`blueprints/`)

Cada arquivo define uma função `registrar(app)` que registra rotas diretamente no app Flask — sem Blueprint class, mantendo `url_for('nome_funcao')` sem namespace.

| Módulo | Entidade |
|--------|----------|
| `professores.py` | Professor |
| `disciplinas.py` | Disciplina |
| `turnos.py` | Turno |
| `turmas.py` | Turma |
| `locais.py` | Local |
| `horarios.py` | Horário de Aula |
| `professor_disciplina.py` | Relação Professor × Disciplina |
| `disponibilidade.py` | Disponibilidade do Professor + Grade |
| `grade_curricular.py` | Grade Curricular |
| `alocacao.py` | Alocação de Aulas |
| `relatorio.py` | Relatório de Grade Horária |

### Modelo de Dados (ordem de dependência)

```
turno → turma
disciplina
professor → professor_disciplina ← disciplina
professor → disponibilidade_professor ← horario_aula
turma + disciplina → grade_curricular
grade_curricular + professor + local + horario_aula → alocacao
```

Entidades base (sem dependências): `professor`, `disciplina`, `turno`, `local`, `horario_aula`.

### Padrão de Rotas

Cada entidade segue o mesmo padrão CRUD em seu módulo:
- `GET /cadastrar_<entidade>` → formulário de criação
- `POST /salvar_<entidade>` → validação + inserção; erros via `flash()` + redirect
- `GET /<entidades>` → listagem
- `GET /editar_<entidade>/<id>` → formulário inline de edição (mesma página da listagem)
- `POST /atualizar_<entidade>/<id>` → atualização
- `POST /deletar_<entidade>/<id>` → exclusão

Entidades especiais com fluxo de dois passos (seleção de turno antes de listar): `alocacao`, `grade_curricular`, `relatorio`.

### Flash Messages

Erros e validações usam `flask.flash(mensagem, 'erro')` + redirect. O `base.html` renderiza automaticamente as mensagens com a classe `.alerta-<categoria>`. Não passar `erro=` para templates — usar sempre flash.

### Acesso ao Banco

Padrão obrigatório em todas as rotas:
```python
from db import conectar

with conectar() as conexao:
    cursor = conexao.cursor()
    cursor.execute("SELECT ... WHERE id = ?", (id,))  # sempre parâmetros posicionais
    conexao.commit()  # apenas em INSERT/UPDATE/DELETE
```

## Personalização Visual

### Template Base

Todo template herda de `base.html`:
```html
{% extends "base.html" %}
{% block titulo %}Nome da Página{% endblock %}
{% block conteudo %}
  <!-- conteúdo aqui -->
{% endblock %}
```

Blocos disponíveis: `titulo`, `conteudo`, `estilos_extra` (CSS no `<head>`), `scripts_extra` (JS antes do `</body>`).

### Tema Noturno

O site usa tema escuro por padrão. Todas as variáveis CSS são dark:

| Variável | Valor | Uso |
|----------|-------|-----|
| `--cor-fundo` | `#0e1117` | Fundo da página |
| `--cor-superficie` | `#1a1d2e` | Cards e tabelas |
| `--cor-superficie-alt` | `#242840` | Inputs, hover de rows |
| `--cor-primaria` | `#5b9bd5` | Títulos, thead, botão primário |
| `--cor-secundaria` | `#7ab3e8` | Hover e foco |
| `--cor-acento` | `#f0a500` | Botão de destaque |
| `--cor-borda` | `#2d3452` | Bordas |
| `--cor-texto` | `#e2e8f0` | Texto principal |
| `--cor-erro` | `#f87171` | Erros e excluir |
| `--cor-sucesso` | `#4ade80` | Badges ativos |

### Classes de Componentes

- **`.card`** — card com borda e sombra (tema escuro)
- **`.cabecalho-pagina`** — flex row com botão ← e h1 no topo de cada página
- **`.layout-duplo`** — grid 2 colunas: formulário + lista lateral (colapsa em mobile)
- **`.tabela-lateral`** — tabela compacta para uso na coluna direita do layout duplo
- **`.seletor-cor`** + **`.btn-cor-preview`** + **`.swatch`** — color picker personalizado para disciplinas
- **`.btn-primario`** / **`.btn-secundario`** / **`.btn-perigo`** / **`.btn-acento`** — variantes de botão
- **`.alerta-erro`** / **`.alerta-sucesso`** — mensagens de feedback (semi-transparentes no dark)
- **`.badge-ativo`** / **`.badge-inativo`** — indicador de status inline
- **`.flex-linha`** — linha flexível com gap
- **`.form-grupo`** — espaçamento padrão entre campos

### Padrão de Navegação

- Todo template tem `<div class="cabecalho-pagina">` com botão ← no topo, antes do `h1`.
- Templates de cadastro usam `class="layout-duplo"` com o formulário à esquerda e a lista existente à direita.
- Para CPF: validação backend exige exatamente 11 dígitos (ou vazio). `cpf or None` para salvar NULL quando vazio.

### Seletor de Cores (Disciplinas)

`cadastro_disciplina.html` e o formulário de edição em `disciplinas.html` usam um color picker customizado:
- `.btn-cor-preview` — círculo clicável que abre o `<input type="color">` nativo
- `.swatch` — paleta de 16 cores predefinidas para disciplinas
- JS em `{% block scripts_extra %}` sincroniza cor entre clique nas swatches e o picker nativo

### Padrão dos Botões de Ação nas Tabelas

O `<td>` de ações **não recebe** `class="flex-linha"` diretamente. Envolva os botões num `<div>` interno:
```html
<td>
    <div class="flex-linha">
        <a href="{{ url_for('editar_X', id=item['id']) }}#form-edicao" class="btn btn-secundario">Editar</a>
        <form action="{{ url_for('deletar_X', id=item['id']) }}" method="POST">
            <button type="submit" class="btn-perigo" onclick="return confirm('...')">Excluir</button>
        </form>
    </div>
</td>
```

- O link "Editar" **sempre** termina com `#form-edicao` para scroll automático até o formulário.
- O formulário de edição inline **sempre** tem `id="form-edicao"` no `<div class="card mt-2">`.
- Botão de excluir **sempre** usa `.btn-perigo` — o CSS usa `:not(.btn-perigo)` para evitar conflito de especificidade.

### Relatório de Impressão

`templates/relatorio.html` é standalone (não herda `base.html`). Requisitos:
- `.celula` deve ter `print-color-adjust: exact` para preservar cores ao imprimir.
- A tabela deve usar `<thead>` para repetição de cabeçalho em múltiplas páginas.
- Botões de ação usam `class="no-print"` para sumir na impressão.

## Melhorias Futuras (Baixa Prioridade)

- **Paginação nas listagens** — professores, disciplinas e alocações podem crescer muito.
- **Exportar relatório em PDF server-side** — o relatório já tem CSS `@media print`; `weasyprint` tornaria a exportação mais robusta.

## Contexto do Projeto

Projeto de extensão universitária. Interface totalmente em Português. Não há autenticação de usuários.
