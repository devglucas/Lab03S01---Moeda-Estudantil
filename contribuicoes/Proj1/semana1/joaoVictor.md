# Semana da entrega no dia 5

contribuicoes
-> historia de caso de uso
-> diagrama de classe

desisoes

-> separar o codigo de envio de email para facilitar se precisars de mudar, deixar generico

-> ter uma classe/tabela para as transaçoes para facilitar quando criar o historico

-> separar logicas, como o envio de moedas, criando uma classe para ela, e ela alterando o aluno. e nao aluno recebendo ou gastando moedas
 -> o mesmo vale para a troca de vantagens, melhor que criar arquivos muito grandes 

uso de IA:
no diagrama de classe usei o GPT para as primeiras versoes do diagrama, no diagrama dele aluno, empresa e professor herdavam de usuario, mas pensei q nao era a melhor solucao, cada um tem seu login