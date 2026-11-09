# Semana da entrega no dia 5

contribuicoes
-> diagrama de caso de uso
-> estrutura inicial de pastas do repositorio
-> readme inicial

desisoes

-> criar um ator generico "Usuario" no caso de uso, com aluno, professor e empresa herdando dele, ja que todos fazem login e consultam extrato

-> deixar o servico de email como um ator externo, porque o envio de email nao é feito pelo sistema em si, e sim por um servico de fora

-> usar include no cadastro de aluno e de empresa para selecionar instituicao e definir login e senha, ja que essas etapas sempre acontecem no cadastro

-> a troca de moedas inclui verificar saldo, gerar cupom e enviar os emails, para deixar claro tudo que acontece em uma troca

-> numerar os casos de uso (R01, R02...) para facilitar ligar com as historias de usuario

uso de IA:
Usei como forma de "brainstorming" para identificar potenciais casos de uso faltantes de acordo com o enunciado do projeto
