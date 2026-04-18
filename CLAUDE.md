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

## Animações e Elementos Visuais (Motion.dev)

A aplicação usa **Motion.dev v11.11.13** via CDN ES module para animações. Não requer instalação — carregado em `base.html`.

### Animações Globais (`base.html`)

Aplicadas automaticamente em todas as páginas:
- Header: slide de cima (`y: [-10, 0]`)
- Linhas de tabela (`tbody tr`): entrada em cascata da esquerda (`stagger(0.04)`)
- Cards (`.card`): fade + slide de baixo (`stagger(0.07)`)
- Título da página (`.cabecalho-pagina h1`): slide da esquerda
- Alertas: fade + scale

CDN import:
```javascript
import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";
```

### Fundo Decorativo

`<div id="fundo-escola">` em `base.html` (classe `no-print`) recebe ícones escolares gerados via JS puro que sobem lentamente com opacidade ~6%. Não interfere com impressão.

### Ícones e Partículas por Entidade

Cada template de listagem adiciona um `.icone-linha` na primeira célula e spawna **partículas flutuantes** ao hover (usando `animate()` do Motion). Timeout de 120ms evita spam.

| Template | Lógica do ícone |
|----------|-----------------|
| `disciplinas.html` | Mapeamento por nome/sigla → 17 categorias (📐 Mat, ⚡ Fís, ⚗️ Qui, 🧬 Bio…) + borda lateral com a cor da disciplina |
| `professores.html` | Sempre 👨‍🏫 + partículas acadêmicas |
| `turmas.html` | `data-turno` → ☀️ matutino / 🌅 vespertino / 🌙 noturno |
| `locais.html` | `data-tipo` → 🔬 lab / 💻 informática / 📚 biblioteca / ⚽ quadra / 🏫 padrão |
| `horarios_aula.html` | `data-inicio` → ícone por faixa de hora (manhã/tarde/noite) |
| `turnos.html` | `data-nome` → ☀️ / 🌅 / 🌙 por nome do turno |

### Classes CSS de Animação

- **`.fundo-escola`** — container fixo z-index:-1, não captura eventos
- **`.item-fundo`** — ícone flutuante; usa `@keyframes flutuar-fundo`
- **`.icone-linha`** — inline em `td:first-child`; escala 1.4× ao hover
- **`.particula-hover`** — `position:fixed`, z-index:9999, removida após animação

## Design Visual — Campo Estelar e Animações

### Fundo (`#fundo-estrelas`)

`#fundo-estrelas` em `base.html` gera um campo de estrelas suave via JS puro:
- Fundo preto `#000` fixo em toda a viewport
- N estrelas (`.estrela`) calculadas por área da tela: `Math.round(W*H/5800)`, min 60, max 220
- Cada estrela tem tamanho aleatório (0.8–2.4px), opacidade variável e animação `estrela-deriva`
- `@keyframes estrela-deriva`: drift suave com `--dx`/`--dy` (±9px) e fade de `--op-a` → `--op-b`
- Duração por estrela: 22–50 s com `animation-delay` negativo aleatório (sem "flash" inicial)

### Botões Flutuantes (`.btn-float`)

Usado na página inicial (`index.html`) para dar vida aos botões de cadastro:
- `.btn-float.btn-primario`: `@keyframes flutuar-suave` — sobe/desce 4px, 3.4 s
- `.btn-float.btn-secundario`: mesma animação, 3.8 s com delay 0.3 s
- `.btn-float.btn-acento`: `@keyframes flutuar-acento` (glow âmbar), 3.2 s
- `animation-play-state: paused` no hover — botão congela ao passar o mouse

### Seções do Index (`.secao-flutuante`)

`index.html` não usa `.card` — usa `.secao-flutuante` e `.secao-titulo` para layout limpo:
```html
<div class="secao-flutuante">
    <h2 class="secao-titulo">🗂️ Cadastros Base</h2>
    <div class="flex-linha mt-1">
        <a href="..." class="btn btn-primario btn-float">Cadastrar X</a>
    </div>
</div>
```

### Botões gerais — Efeito Shine

Todos os botões têm shine sweep no hover via `::after`:
- Gradiente diagonal `rgba(255,255,255,0.1)` percorre o botão (`left: -110% → 160%`)
- Transição `cubic-bezier(0.175, 0.885, 0.32, 1.275)` em `background-color` e `box-shadow`
- **Sem** `transform` no hover (mantém fluido, sem "pulo")

### Padrão para novos templates com ícones

```html
{% block scripts_extra %}
<script type="module">
import { animate } from "https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm";

function spawnParticulas(particulas, rect) {
    for (let i = 0; i < 5; i++) {
        const el = document.createElement('span');
        el.textContent = particulas[Math.floor(Math.random() * particulas.length)];
        el.className = 'particula-hover';
        el.style.left = (rect.left + Math.random() * rect.width) + 'px';
        el.style.top  = (rect.top  + rect.height / 2) + 'px';
        el.style.fontSize = (12 + Math.random() * 8) + 'px';
        document.body.appendChild(el);
        animate(el,
            { y:[0, -(40 + Math.random() * 45)], opacity:[0.9, 0], scale:[1, 0.5] },
            { duration: 0.85 + Math.random() * 0.4, delay: i * 0.08, ease:'easeOut' }
        ).then(() => el.remove());
    }
}

document.querySelectorAll('tbody tr[data-X]').forEach(tr => {
    /* injetar icone-linha + registrar hover com spawnParticulas */
});
</script>
{% endblock %}
```

Adicionar `data-*` aos `<tr>` no Jinja2: `<tr data-X="{{ item['campo'] }}">`.

## Autenticação e Controle de Acesso

### Perfis e Permissões

| Funcionalidade | diretor | secretaria | professor |
|---|---|---|---|
| Login / logout | ✅ | ✅ | ✅ |
| Editar próprio perfil | ✅ | ✅ | ✅ |
| Ver relatório de horários | ✅ | ✅ | ✅ |
| Listar / CRUD entidades | ✅ | ✅ | ❌ |
| Gerenciar usuários | ✅ | ❌ | ❌ |

### Tabela `usuario`
```sql
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('diretor', 'secretaria', 'professor')),
    id_professor INTEGER,
    primeiro_login INTEGER DEFAULT 1 CHECK (primeiro_login IN (0, 1)),
    ativo INTEGER DEFAULT 1 CHECK (ativo IN (0, 1)),
    FOREIGN KEY (id_professor) REFERENCES professor(id_professor)
);
```

### Arquivo `auth.py`
- `usuario_logado()` → dict `{id, nome, perfil, id_professor, primeiro_login}` ou `None`
- `requer_login` → decorator; redireciona para `/login` se não autenticado
- `requer_perfil(*perfis)` → decorator; verifica se `session['usuario_perfil']` está nos perfis permitidos
- Senhas: `werkzeug.security.generate_password_hash` / `check_password_hash`

### Decorators nos blueprints
```python
from auth import requer_perfil   # ou requer_login para relatorio

@app.route('/rota')
@requer_perfil('diretor', 'secretaria')  # todos blueprints exceto relatorio
def view():
    ...
```
- `relatorio.py` usa apenas `@requer_login`
- `blueprints/usuarios.py` usa `@requer_perfil('diretor')` em todas as rotas

### Context Processor (rotas.py)
```python
@app.context_processor
def injetar_usuario():
    return dict(usuario_atual=auth.usuario_logado())
```
`usuario_atual` disponível em todos os templates (usado em `base.html` para nav dinâmica).

### Primeiro Login
Quando `usuario['primeiro_login'] == 1`: redirect automático para `/meu_perfil` após login.
Ao salvar nova senha em `/meu_perfil`, campo `primeiro_login` é zerado.

### Seeds padrão (criar_banco.py)
Inseridos somente se tabela `usuario` estiver vazia:
- `diretor@escola.com` / `diretor123` → perfil diretor
- `secretaria@escola.com` / `secretaria123` → perfil secretaria

### Rotas de auth (rotas.py)
- `GET/POST /login` → login
- `POST /logout` → limpa sessão
- `GET/POST /meu_perfil` → editar próprio perfil (requer_login)
- `GET / ` → index (requer_login)

## Melhorias Futuras (Baixa Prioridade)

- **Paginação nas listagens** — professores, disciplinas e alocações podem crescer muito.
- **Exportar relatório em PDF server-side** — o relatório já tem CSS `@media print`; `weasyprint` tornaria a exportação mais robusta.

## Contexto do Projeto

Projeto de extensão universitária. Interface totalmente em Português.
