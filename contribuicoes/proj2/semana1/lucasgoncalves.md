# Semana de 26/10 ate 09/11

contribuicoes
-> hierarquia de transacao no back: Transacao como superclasse de EnvioMoeda e TrocaVantagem

-> ajuste do envio de moedas: uso dos repositories, validacao dos campos e mensagem de saldo insuficiente

-> configuracao do envio de email por variaveis de ambiente, com .env.example

-> templates de email separados para o professor (confirmacao do envio) e para o aluno (aviso de recebimento)

-> envio dos emails em segundo plano, com nova tentativa quando o servidor recusa por limite de envios

-> tela de extrato para professor e aluno

-> edicao e exclusao de professor no back e correcoes na tela de professores

-> correcao de bugs: rota de envio de moedas quebrada, erro 500 ao excluir aluno com transacoes, horario errado nas transacoes

-> testes automatizados de professor, envio de moedas, saldo insuficiente, atomicidade, extrato e emails

-> atualizacao do readme, do modelo ER e dos diagramas de classe e de componentes

decisões

-> nao fazer login nessa sprint, o usuario e escolhido em uma lista na tela

-> criar a hierarquia de transacao agora, para o extrato do aluno ja nascer preparado para as trocas por vantagem

-> deixar o aluno na tabela de transacoes, porque toda transacao envolve um aluno, assim o extrato dele é uma consulta so

-> debito, credito e registro do envio no mesmo commit, se algo falhar nada é gravado

-> o texto dos emails fica em templates, fora do codigo de negocio

-> falha no email nao desfaz o envio de moedas, o erro fica registrado no log do back

-> usar o sandbox do Mailtrap em desenvolvimento e deixar as credenciais no .env, fora do git

-> nao deixar excluir aluno com transacoes nem professor que ja enviou moedas, para nao perder o historico do extrato

uso de IA:
Assistente de IA para ajudar a implementar as funcionalidades da sprint e encontrar e corrigir bugs.
