# Como Usar — Sistema de Horários Escolares

Guia rápido para rodar o sistema. Não precisa instalar Python nem MySQL:
o **Docker** cuida de tudo.

---

## 1. Pré-requisito (instalar uma vez)

Instale o **Docker Desktop**:

- **Windows / Mac:** baixe em <https://www.docker.com/products/docker-desktop/>,
  instale e **abra o Docker Desktop** (deixe ele rodando).
- **Linux:** instale o `docker` e o `docker compose` pela sua distribuição.

> Só precisa fazer isso uma vez, na primeira máquina.

---

## 2. Ligar o sistema

Abra um terminal **dentro da pasta do projeto** e rode:

```bash
docker compose up --build
```

Na primeira vez ele baixa tudo e monta o banco (pode levar alguns minutos).
Quando aparecer a mensagem `Running on http://0.0.0.0:5000`, está no ar.

> Deixe essa janela do terminal **aberta** — ela é o sistema rodando.

---

## 3. Usar o sistema

Abra o navegador em:

### 👉 <http://localhost:5000>

**Login:**

| Campo | Valor          |
|-------|----------------|
| Email | `admin@escola.com` |
| Senha | `admin123`     |

Depois de entrar, siga a ordem do menu para montar os horários:

1. Cadastrar **professores**
2. Cadastrar **disciplinas**
3. Cadastrar **turmas**
4. Cadastrar **horários de aula**
5. Cadastrar a **disponibilidade** de cada professor
6. **Montar a grade** de cada turma (arrastando as aulas)
7. **Imprimir o relatório** de cada turma (1 página, dá para salvar em PDF)

---

## 4. Desligar o sistema

Na janela do terminal onde ele está rodando, aperte:

```
Ctrl + C
```

Ou, em outro terminal na mesma pasta:

```bash
docker compose down
```

> Os dados ficam **salvos** mesmo depois de desligar. Da próxima vez, é só rodar
> `docker compose up` de novo (sem o `--build`) que tudo volta como estava.

---

## 5. Ver o banco de dados (opcional)

Se quiser olhar as tabelas por dentro, abra:

### 👉 <http://localhost:8082>

| Campo    | Valor          |
|----------|----------------|
| Usuário  | `root`         |
| Senha    | `rootsenha`    |

O banco do sistema é o **`horarios_escola`**, na lista à esquerda.

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| "Cannot connect to the Docker daemon" | O Docker Desktop não está aberto. Abra e espere ficar verde. |
| A porta 5000 já está em uso | Feche o outro programa que usa a 5000, ou peça ajuda para trocar a porta. |
| Esqueci se está ligado | Rode `docker compose ps` na pasta do projeto — mostra o que está no ar. |
| Quero começar do zero (apagar tudo) | `docker compose down -v` apaga **todos os dados** e recria limpo no próximo `up`. |
