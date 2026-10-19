-- =====================================================================
-- Modelo Entidade-Relacionamento - Sistema de Moeda Estudantil
-- Banco: SQLite
--
-- As tabelas marcadas como [IMPLEMENTADA] são geradas automaticamente
-- pelo ORM (Flask-SQLAlchemy) a partir dos models em codigo/back/app/models.
-- As marcadas como [PLANEJADA] serão implementadas nas próximas sprints.
--
-- Herança: Aluno, Professor e EmpresaParceira herdam de Usuario usando a
-- estratégia "joined table" (uma tabela por subtipo). A tabela usuarios
-- guarda as credenciais comuns e cada perfil tem a sua tabela, cuja chave
-- primária é também chave estrangeira para usuarios.id. Assim o login é
-- único entre todos os tipos de usuário.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- [IMPLEMENTADA] Superclasse de todos os perfis que fazem login.
-- tipo é o discriminador da herança: 'aluno' | 'professor' | 'empresa'.
-- A senha é guardada como hash, nunca em texto puro.
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
    id          INTEGER      NOT NULL PRIMARY KEY,
    login       VARCHAR(50)  NOT NULL UNIQUE,
    senha_hash  VARCHAR(255) NOT NULL,
    tipo        VARCHAR(20)  NOT NULL
);

-- ---------------------------------------------------------------------
-- [IMPLEMENTADA] Instituições de ensino pré-cadastradas no sistema.
-- ---------------------------------------------------------------------
CREATE TABLE instituicoes_ensino (
    id    INTEGER      NOT NULL PRIMARY KEY,
    nome  VARCHAR(160) NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- [IMPLEMENTADA] Alunos. Relacionamento N:1 com instituicoes_ensino.
-- O saldo começa em 0 e só muda por transações (envio de moedas e troca
-- por vantagem). CPF é guardado só com os dígitos.
-- ---------------------------------------------------------------------
CREATE TABLE alunos (
    id              INTEGER      NOT NULL PRIMARY KEY,
    nome            VARCHAR(120) NOT NULL,
    email           VARCHAR(160) NOT NULL UNIQUE,
    cpf             VARCHAR(11)  NOT NULL UNIQUE,
    rg              VARCHAR(20)  NOT NULL,
    endereco        VARCHAR(255) NOT NULL,
    curso           VARCHAR(120) NOT NULL,
    saldo           INTEGER      NOT NULL DEFAULT 0,
    instituicao_id  INTEGER      NOT NULL,
    FOREIGN KEY (id)             REFERENCES usuarios (id),
    FOREIGN KEY (instituicao_id) REFERENCES instituicoes_ensino (id)
);

-- ---------------------------------------------------------------------
-- [PLANEJADA] Professores. Relacionamento N:1 com instituicoes_ensino.
-- Recebem 1.000 moedas a cada semestre (acumulativas).
-- ---------------------------------------------------------------------
CREATE TABLE professores (
    id              INTEGER      NOT NULL PRIMARY KEY,
    nome            VARCHAR(120) NOT NULL,
    email           VARCHAR(160) NOT NULL UNIQUE,
    cpf             VARCHAR(11)  NOT NULL UNIQUE,
    departamento    VARCHAR(120) NOT NULL,
    saldo           INTEGER      NOT NULL DEFAULT 0,
    instituicao_id  INTEGER      NOT NULL,
    FOREIGN KEY (id)             REFERENCES usuarios (id),
    FOREIGN KEY (instituicao_id) REFERENCES instituicoes_ensino (id)
);

-- ---------------------------------------------------------------------
-- [IMPLEMENTADA] Empresas parceiras. CNPJ é guardado só com os dígitos.
-- ---------------------------------------------------------------------
CREATE TABLE empresas_parceiras (
    id     INTEGER      NOT NULL PRIMARY KEY,
    nome   VARCHAR(120) NOT NULL,
    email  VARCHAR(160) NOT NULL UNIQUE,
    cnpj   VARCHAR(14)  NOT NULL UNIQUE,
    FOREIGN KEY (id) REFERENCES usuarios (id)
);

-- ---------------------------------------------------------------------
-- [PLANEJADA] Vantagens oferecidas pelas empresas parceiras.
-- Relacionamento N:1 com empresas_parceiras. foto guarda o caminho/URL.
-- ---------------------------------------------------------------------
CREATE TABLE vantagens (
    id            INTEGER      NOT NULL PRIMARY KEY,
    nome          VARCHAR(120) NOT NULL,
    descricao     TEXT         NOT NULL,
    foto          VARCHAR(255),
    custo_moedas  INTEGER      NOT NULL CHECK (custo_moedas > 0),
    empresa_id    INTEGER      NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES empresas_parceiras (id)
);

-- ---------------------------------------------------------------------
-- [PLANEJADA] Envio de moedas de um professor para um aluno.
-- Relacionamentos N:1 com professores e com alunos. O motivo
-- (reconhecimento) é obrigatório.
-- ---------------------------------------------------------------------
CREATE TABLE envios_moeda (
    id            INTEGER  NOT NULL PRIMARY KEY,
    data          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantidade    INTEGER  NOT NULL CHECK (quantidade > 0),
    motivo        TEXT     NOT NULL,
    professor_id  INTEGER  NOT NULL,
    aluno_id      INTEGER  NOT NULL,
    FOREIGN KEY (professor_id) REFERENCES professores (id),
    FOREIGN KEY (aluno_id)     REFERENCES alunos (id)
);

-- ---------------------------------------------------------------------
-- [PLANEJADA] Troca de moedas por uma vantagem.
-- Relacionamentos N:1 com alunos e com vantagens. codigo é o cupom
-- enviado por e-mail ao aluno e à empresa para conferência na troca.
-- ---------------------------------------------------------------------
CREATE TABLE trocas_vantagem (
    id           INTEGER     NOT NULL PRIMARY KEY,
    data         DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantidade   INTEGER     NOT NULL CHECK (quantidade > 0),
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    aluno_id     INTEGER     NOT NULL,
    vantagem_id  INTEGER     NOT NULL,
    FOREIGN KEY (aluno_id)    REFERENCES alunos (id),
    FOREIGN KEY (vantagem_id) REFERENCES vantagens (id)
);
