# Plataforma de Gestão de Reembolsos Corporativos - NexusCorp

## 1. Descrição da Solução
Esta API REST foi desenvolvida em Python (FastAPI) para centralizar a gestão de reembolsos da NexusCorp. O sistema resolve problemas de visibilidade indevida, aprovações fora de alçada e falta de rastreabilidade, implementando um fluxo rigoroso de três perfis (Colaborador, Gestor e Financeiro) com banco de dados relacional (SQLite).

## 2. Modelo de Dados
- Departamento: Armazena os setores da empresa.
- Usuario: Possui nome, e-mail (único), senha (criptografada), perfil e vínculo com um departamento.
- SolicitacaoReembolso: Vinculada a um usuário. Contém categoria, valor, data, justificativa, comprovante e situação.
- HistoricoAnalise: Registra as decisões tomadas, data, observação e o responsável.

## 3. Contrato das Principais Operações
- POST /auth/login: Autentica o usuário e gera o Token JWT.
- POST /colaborador/solicitacoes: Cria uma nova despesa em rascunho.
- POST /colaborador/solicitacoes/{id}/enviar: Envia o rascunho para a análise do gestor.
- GET /gestor/solicitacoes: Lista despesas pendentes do departamento do gestor.
- POST /gestor/solicitacoes/{id}/aprovar: Aprova a despesa e envia ao financeiro.
- GET /financeiro/solicitacoes: Lista despesas aguardando análise final.
- POST /financeiro/solicitacoes/{id}/pagar: Registra a conclusão do pagamento.

## 4. Matriz de Permissões
- Colaborador: Acessa apenas as rotas /colaborador/...
- Gestor: Acessa apenas as rotas /gestor/...
- Financeiro: Acessa apenas as rotas /financeiro/...

## 5. Regras de Negócio Implementadas
- RN02 (Confidencialidade): Filtro por ID do solicitante no banco.
- RN03 (Responsabilidade depto): Valida o departamento do gestor.
- RN04 (Valores): Validação de valor maior que zero.
- RN05 (Duplicidade): Busca no banco pela referência do comprovante antes de criar.
- RN07 (Alteração): Bloqueia edições se a situação não for "RASCUNHO".
- RN08 e RN10 (Sequência): Bloqueia aprovações/pagamentos fora de ordem.
- RN09 (Segregação): Impede aprovar a própria despesa.

## 6. Decisões de Segurança
- Senhas: Criptografadas com Bcrypt.
- Autenticação: Via Token JWT com tempo de expiração.
- Controle de Acesso: Dependências do FastAPI (require_role) garantem que apenas perfis autorizados acessem as rotas.