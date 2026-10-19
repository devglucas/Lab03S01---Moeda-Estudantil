# Semana da entrega no dia 19

contribuicoes
-> correcao do back que nao estava subindo (faltava o arquivo de validacao, funcao buscar duplicada nos controllers, funcao texto que nao existia)
-> validacao dos campos no cadastro de aluno e empresa
-> CNPJ na empresa parceira
-> seed com as instituicoes de ensino iniciais
-> testes automatizados dos CRUDs com pytest
-> front-end com React e Vite, com as telas de cadastro, listagem, edicao e exclusao de aluno e empresa
-> mascaras de CPF, RG e CNPJ no front
-> modelo entidade-relacionamento 
-> atualizacao do readme 

decisões

-> manter o ORM (SQLAlchemy) em vez de DAO com SQL manual

-> usar o email como login, para o usuario nao precisar preencher dois campos parecidos. o email fica unico entre aluno, professor e empresa

-> front separado em React consumindo a API, em vez de paginas renderizadas pelo Flask

-> a pontuacao de CPF, RG e CNPJ é so visual no front, o back recebe e guarda so os numeros

-> tirar o banco (moedas.db) do git, ele é criado sozinho quando o back sobe

-> no modelo ER o cupom virou uma coluna da troca de vantagem, ja que é 1 para 1, e as tabelas que ainda nao existem no codigo aparecem como planejadas

-> os testes usam um banco em memoria para nao apagar o banco de desenvolvimento

uso de IA:
Assistente de IA para ajudar a implementar as funcionalidades da sprint. 
