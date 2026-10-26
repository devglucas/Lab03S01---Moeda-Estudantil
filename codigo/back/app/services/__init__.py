"""Camada de serviço: regras de negócio e validações.

Os controllers só traduzem HTTP <-> Python e delegam para cá. Os services
usam os repositórios para ler e gravar, e sinalizam problemas lançando os
erros de ``app.services.erros``, que viram respostas JSON com o status certo.
"""
