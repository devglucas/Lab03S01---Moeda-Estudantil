# 🏷️ Sistema de Moeda Estudantil 👨‍💻

Pretende-se desenvolver um sistema para estimular o reconhecimento do mérito estudantil por meio de uma moeda virtual. Essa moeda pode ser distribuída por professores aos seus alunos e trocada pelos alunos por produtos e descontos em empresas parceiras. Pretende-se desenvolver o sistema ao longo de três releases, a arquitetura usada será a padrão MVC e tudo será documentado por meio de diagramas de caso de uso, diagramas de classe e diagramas de componentes.

---

## 📚 Índice
- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Arquitetura](#-arquitetura)
  - [Diagramas](#diagramas)
- [Estratégia de Acesso ao Banco de Dados](#-estratégia-de-acesso-ao-banco-de-dados)
- [Endpoints da API](#-endpoints-da-api)
- [Instalação e Execução](#-instalação-e-execução)
  - [Pré-requisitos](#pré-requisitos)
  - [Variáveis de Ambiente](#-variáveis-de-ambiente)
  - [Instalação de Dependências](#-instalação-de-dependências)
  - [Como Executar a Aplicação](#-como-executar-a-aplicação)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Testes](#-testes)
- [Documentações utilizadas](#-documentações-utilizadas)
- [Autores](#-autores)
- [Contribuição](#-contribuição)
- [Agradecimentos](#-agradecimentos)
- [Licença](#-licença)

---

## 📝 Sobre o Projeto

Projeto desenvolvido na disciplina de **Laboratório de Desenvolvimento de Software** do curso de Engenharia de Software da PUC Minas.

O sistema de moeda estudantil incentiva o reconhecimento do mérito dos alunos. Ele envolve três perfis de usuário:

- **Aluno:** se cadastra informando seus dados e sua instituição de ensino, recebe moedas dos professores e pode trocá-las por vantagens.
- **Professor:** recebe 1.000 moedas por semestre (acumulativas) e as distribui aos alunos, sempre informando o motivo do reconhecimento.
- **Empresa parceira:** se cadastra no sistema e oferece vantagens (produtos ou descontos) que podem ser resgatadas com moedas.

As instituições de ensino são pré-cadastradas. O desenvolvimento acontece em sprints, e cada sprint entrega uma parte do sistema junto com a documentação correspondente.

---

## ✨ Funcionalidades Principais

**Implementadas**

- 🎓 **CRUD de Aluno:** cadastro, listagem, edição e exclusão de alunos, com validação de CPF, e-mail e instituição de ensino.
- 🏢 **CRUD de Empresa Parceira:** cadastro, listagem, edição e exclusão de empresas, com validação de CNPJ e e-mail.
- 🏫 **Instituições de Ensino:** instituições pré-cadastradas automaticamente na primeira execução.
- 🔐 **Senhas protegidas:** as senhas são armazenadas apenas como hash.

**Planejadas (próximas sprints)**

- 🔑 Autenticação de alunos, professores e empresas.
- 🪙 Envio de moedas do professor para o aluno, com motivo obrigatório.
- 🎁 Cadastro de vantagens pelas empresas parceiras.
- 🔄 Troca de moedas por vantagens, com geração de cupom.
- 📄 Extrato de transações para alunos e professores.
- 📨 Notificações por e-mail (recebimento de moedas e cupom de troca).

---

## 🛠 Tecnologias Utilizadas

### 💻 Front-end

* **Biblioteca:** React 19.1
* **Linguagem:** JavaScript (ES6+)
* **Estilização:** CSS puro
* **Build Tool:** Vite 7.1

### 🖥️ Back-end

* **Linguagem:** Python 3.11+
* **Framework:** Flask 3.0
* **Banco de Dados:** SQLite
* **ORM:** SQLAlchemy 2 (via Flask-SQLAlchemy 3.1)
* **CORS:** Flask-Cors 4.0
* **Testes:** pytest 8.3

---

## 🏗 Arquitetura

O sistema segue a arquitetura **MVC**, com o back-end e o front-end separados e comunicando-se por uma **API REST** em JSON.

- **Model** (`codigo/back/app/models`): classes que representam as entidades do domínio e são mapeadas para tabelas do banco pelo ORM.
- **Controller** (`codigo/back/app/controllers`): um *blueprint* do Flask por recurso (alunos, empresas, instituições). Recebe as requisições HTTP, valida os dados, usa os models para ler e gravar no banco e devolve JSON.
- **View** (`codigo/front`): aplicação React que consome a API e exibe as telas de cadastro e listagem.

Fluxo de uma requisição:

```
Tela React  ->  fetch (src/api.js)  ->  Controller Flask  ->  Model (SQLAlchemy)  ->  SQLite
```

### Diagramas

| Diagrama | Arquivo |
| :--- | :--- |
| Casos de uso | [`docs/caso_de_uso.png`](docs/caso_de_uso.png) |
| Classes | [`docs/diagrama_de_classe.png`](docs/diagrama_de_classe.png) |
| Modelo Entidade-Relacionamento | [`docs/modelo-er.png`](docs/modelo-er.png) (script SQL comentado em [`docs/modelo-er.sql`](docs/modelo-er.sql)) |

As histórias de usuário estão em [`docs/historias-de-usuario.md`](docs/historias-de-usuario.md).

---

## 💾 Estratégia de Acesso ao Banco de Dados

O grupo escolheu usar um **ORM (Object-Relational Mapping)**, o **SQLAlchemy**, integrado ao Flask pelo **Flask-SQLAlchemy**.

**Por que ORM e não DAO com SQL manual**

- Cada classe do domínio (`Aluno`, `EmpresaParceira`, `InstituicaoEnsino`) é mapeada diretamente para uma tabela, sem escrever SQL para as operações básicas de CRUD.
- As tabelas são criadas automaticamente a partir dos models na inicialização (`db.create_all()`), o que mantém o código e o banco sempre consistentes.
- As consultas são feitas com objetos Python (`Aluno.query.filter_by(cpf=cpf)`), o que evita erros de digitação em SQL e protege contra SQL injection.
- O grupo já tinha experiência com essa abordagem em projetos anteriores, o que acelera o desenvolvimento.

**Como está organizado**

- `app/extensions.py`: instância única do `SQLAlchemy`, compartilhada por toda a aplicação.
- `app/models/`: as entidades persistentes. Cada model herda de `db.Model` e declara suas colunas, chaves e relacionamentos.
- `app/__init__.py`: configura a conexão (`SQLALCHEMY_DATABASE_URI`), cria as tabelas e cadastra as instituições iniciais (`app/seed.py`).

**Mapeamento da herança**

`Aluno`, `Professor` e `EmpresaParceira` herdam de `Usuario`. Foi usada a estratégia **joined table** (uma tabela por subtipo): a tabela `usuarios` guarda o login, o hash da senha e o tipo do usuário, e cada perfil tem a sua própria tabela, cuja chave primária também é chave estrangeira para `usuarios.id`. Assim o login é único entre todos os perfis, e cada tabela guarda apenas os campos do seu perfil.

**Banco de dados**

O banco é o **SQLite**, gravado no arquivo `codigo/back/moedas.db`. Ele não precisa de instalação nem de servidor, o que simplifica a configuração do ambiente de cada integrante. O arquivo não é versionado e é criado automaticamente na primeira execução. Como o acesso passa pelo ORM, trocar para outro banco (por exemplo, PostgreSQL) exige apenas mudar a variável `DATABASE_URL`.

O modelo completo, incluindo as tabelas planejadas para as próximas sprints, está em [`docs/modelo-er.png`](docs/modelo-er.png).

---

## 🔌 Endpoints da API

URL base: `http://localhost:5000/api`

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/alunos` | Lista os alunos |
| `GET` | `/alunos/{id}` | Busca um aluno |
| `POST` | `/alunos` | Cadastra um aluno |
| `PUT` | `/alunos/{id}` | Atualiza um aluno (senha opcional) |
| `DELETE` | `/alunos/{id}` | Remove um aluno |
| `GET` | `/empresas` | Lista as empresas parceiras |
| `GET` | `/empresas/{id}` | Busca uma empresa parceira |
| `POST` | `/empresas` | Cadastra uma empresa parceira |
| `PUT` | `/empresas/{id}` | Atualiza uma empresa parceira (senha opcional) |
| `DELETE` | `/empresas/{id}` | Remove uma empresa parceira |
| `GET` | `/instituicoes` | Lista as instituições de ensino |
| `GET` | `/instituicoes/{id}` | Busca uma instituição |
| `POST` | `/instituicoes` | Cadastra uma instituição |
| `PUT` | `/instituicoes/{id}` | Atualiza uma instituição |
| `DELETE` | `/instituicoes/{id}` | Remove uma instituição sem alunos vinculados |

Em caso de erro, a API responde com `{"erro": "mensagem"}` e, quando há campos inválidos, `{"erro": "...", "campos": {"campo": "mensagem"}}`. Exemplos de corpo das requisições estão em [`JSONTESTES.txt`](JSONTESTES.txt).

---

## 🔧 Instalação e Execução

### Pré-requisitos

* **Python:** versão 3.11 ou superior (back-end)
* **Node.js:** versão 18 ou superior, com npm (front-end)
* **Git**

### 🔑 Variáveis de Ambiente

Nenhuma variável é obrigatória para rodar localmente. Os valores padrão já funcionam.

**Back-end** (opcional, em `codigo/back/.env`):

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `DATABASE_URL` | URL de conexão do banco | SQLite em `codigo/back/moedas.db` |
| `FRONTEND_ORIGIN` | Origem liberada no CORS | `http://localhost:5173` |

**Front-end** (opcional, em `codigo/front/.env.local`, veja `codigo/front/.env.example`):

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `VITE_API_URL` | URL base da API | `http://localhost:5000/api` |

### 📦 Instalação de Dependências

**Back-end**

```bash
cd codigo/back
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Front-end**

```bash
cd codigo/front
npm install
```

### ⚡ Como Executar a Aplicação

Use dois terminais.

**Terminal 1: Back-end (Flask)**

```bash
cd codigo/back
source venv/bin/activate        # Windows: venv\Scripts\activate
python run.py
```

A API sobe em `http://localhost:5000`. Na primeira execução o banco `moedas.db` é criado e as instituições de ensino são cadastradas.

**Terminal 2: Front-end (React, Vite)**

```bash
cd codigo/front
npm run dev
```

Acesse `http://localhost:5173` no navegador.

---

## 📂 Estrutura de Pastas

```
.
├── README.md
├── JSONTESTES.txt                 # 🧪 Exemplos de JSON para testar a API.
├── contribuicoes/                 # 📝 Registro semanal das contribuições.
├── docs/                          # 📚 Diagramas e documentação.
│   ├── caso_de_uso.puml / .png
│   ├── diagrama_de_classe.puml / .png
│   ├── modelo-er.puml / .png / .sql
│   └── historias-de-usuario.md
│
└── codigo/
    ├── back/                      # 🖥️ API Flask
    │   ├── run.py                 # 🚀 Ponto de entrada do back-end.
    │   ├── requirements.txt       # 📦 Dependências Python.
    │   ├── app/
    │   │   ├── __init__.py        # ⚙️ Criação da aplicação, banco e CORS.
    │   │   ├── extensions.py      # 🗄️ Instância do SQLAlchemy.
    │   │   ├── seed.py            # 🌱 Instituições de ensino iniciais.
    │   │   ├── validacao.py       # ✅ Funções de validação.
    │   │   ├── models/            # 🧬 Entidades persistentes (ORM).
    │   │   └── controllers/       # 🎮 Endpoints REST (blueprints).
    │   └── tests/                 # 🧪 Testes automatizados (pytest).
    │
    └── front/                     # 💻 Aplicação React
        ├── index.html
        ├── package.json
        ├── vite.config.js
        └── src/
            ├── main.jsx           # 🚀 Ponto de entrada do React.
            ├── App.jsx            # 🧭 Navegação entre as telas.
            ├── api.js             # 🔌 Chamadas HTTP para a API.
            ├── formatacao.js      # 🛠️ Formatação de CPF e CNPJ.
            ├── styles.css         # 🎨 Estilos globais.
            ├── components/        # 🧱 Componentes reutilizáveis.
            └── pages/             # 📄 Telas de alunos e empresas.
```

---

## 🧪 Testes

Os testes automatizados do back-end usam **pytest** e rodam em um banco SQLite em memória, sem afetar o `moedas.db`.

```bash
cd codigo/back
source venv/bin/activate
python -m pytest
```

Eles cobrem o CRUD completo de aluno e de empresa parceira, a validação de campos obrigatórios, CPF e CNPJ, e as regras de unicidade (login, e-mail, CPF e CNPJ).

---

## 🔗 Documentações utilizadas

* 📖 **Back-end:** [Documentação Oficial do **Flask**](https://flask.palletsprojects.com/)
* 📖 **ORM:** [Documentação do **Flask-SQLAlchemy**](https://flask-sqlalchemy.readthedocs.io/) e do [**SQLAlchemy**](https://docs.sqlalchemy.org/)
* 📖 **Front-end:** [Documentação Oficial do **React**](https://react.dev/reference/react)
* 📖 **Build Tool:** [Guia de Configuração do **Vite**](https://vitejs.dev/config/)
* 📖 **Diagramas:** [Documentação do **PlantUML**](https://plantuml.com/)
* 📖 **Guia de Estilo:** [**Conventional Commits** (Padrão de Mensagens)](https://www.conventionalcommits.org/en/v1.0.0/)

---

## 👥 Autores

| 👤 Nome | 🖼️ Foto | :octocat: GitHub |
|---------|----------|-----------------|
| Lucas Gonçalves dos Santos | <div align="center"><img src="https://github.com/devglucas.png" width="70px" height="70px"></div> | <div align="center"><a href="https://github.com/devglucas"><img src="https://joaopauloaramuni.github.io/image/github6.png" width="50px" height="50px"></a></div> |
| João Victor | <div align="center"><img src="https://github.com/jaofr.png" width="70px" height="70px"></div> | <div align="center"><a href="https://github.com/jaofr"><img src="https://joaopauloaramuni.github.io/image/github6.png" width="50px" height="50px"></a></div> |

---

## 🤝 Contribuição
Guia para contribuições ao projeto.

1.  Faça um `fork` do projeto.
2.  Crie uma branch para sua feature (`git checkout -b feature/minha-feature`).
3. Commit suas mudanças (`git commit -m 'feat: Adiciona nova funcionalidade X'`). **(Utilize [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/))**
4.  Faça o `push` para a branch (`git push origin feature/minha-feature`).
5.  Abra um **Pull Request (PR)**.

---

## 🙏 Agradecimentos
Em ambiente acadêmico, citar fontes e inspirações é crucial (integridade acadêmica). Em ambiente profissional, mostra humildade e conexão com a comunidade.

Gostaria de agradecer aos seguintes canais e pessoas que foram fundamentais para o desenvolvimento deste projeto:

* [**Engenharia de Software PUC Minas**](https://www.instagram.com/engsoftwarepucminas/) - Pelo apoio institucional, estrutura acadêmica e fomento à inovação e boas práticas de engenharia.
* [**Prof. Dr. João Paulo Aramuni**](https://github.com/joaopauloaramuni) - Pelos valiosos ensinamentos sobre **Arquitetura de Software** e **Padrões de Projeto**.
* [**Fernanda Kipper**](https://www.instagram.com/kipper.dev/) - Pelos valiosos ensinamentos em **Desenvolvimento Web**, **DevOps** e melhores práticas em **Front-end**.
* [**Rodrigo Branas**](https://branas.io/) - Pela didática excepcional em **Clean Architecture** e **Clean Code**.
* [**Código Fonte TV**](https://codigofonte.tv/) - Pelo vasto conteúdo e cobertura de notícias, tutoriais e apoio à comunidade de **Desenvolvimento Web**.

---

## 📄 Licença

Este projeto é distribuído sob a **[Licença MIT](https://github.com/joaopauloaramuni/laboratorio-de-desenvolvimento-de-software/blob/main/LICENSE)**.

---
