# Guia de estudo e demonstração

Este guia não substitui seu domínio. Leia cada módulo, execute-o, modifique um comportamento e explique o efeito antes de entregar. Se não consegue explicar um trecho, estude e simplifique-o. Declare como usou IA.

## Demonstração de cinco minutos

1. **Problema e cidadão (40 s).** Moradores de regiões sujeitas a alagamentos; evidência IBGE/Cemaden de 2018, com base de 2010; inspiração de zeladoria colaborativa e ODS 11/13. Não afirmar que o dado é atual ou que houve entrevista.
2. **Consulta (40 s).** Abrir painel, selecionar município, mostrar setores fictícios, filtros, contadores e atribuição Open-Meteo. Distinguir chuva prevista e enchente: o protótipo não prevê inundação.
3. **CRUD (90 s).** Copiar chave local sem projetar o `.env`; registrar, editar status, confirmar exclusão. Alternativamente executar `python -m scripts.demonstrar_api` e explicar 200/201/204/400/401.
4. **Código e segurança (60 s).** Mostrar rota Flask, allowlists, um `cursor.execute(sql, parametros)`, conexão/transação e tratamento de falha. Mostrar log com data/hora, ação e resultado, sem segredo.
5. **TCP (30 s).** Executar cliente com servidor ativo, mostrar contagens por status e explicar token próprio, bytes, newline e fragmentação.
6. **Validação e limite (40 s).** Mostrar resultados de testes e três ameaças. Explicar que testes técnicos não validam a utilidade social; ainda faltam usuários, moderação e operação real.

## Perguntas para você conseguir responder

| Pergunta | Ponto para estudar no código |
|---|---|
| Por que Flask? | Rotas HTTP, objetos request/response, fábrica create_app, servidor WSGI |
| Por que MySQL e não arquivo JSON? | Persistência, concorrência, restrições e consultas; log continua em arquivo por exigência |
| Onde estão GET/POST/PUT/DELETE? | app/__init__.py; verbo muda semântica, payload e status |
| Qual diferença entre 200, 201 e 204? | Consulta/atualização; criação com Location; exclusão sem corpo |
| O que faz `%s`? | É placeholder do driver, não interpolação Python; o valor é enviado separadamente do SQL |
| Como um erro desfaz uma operação? | Context manager em db.py executa rollback antes de fechar a conexão |
| Por que SQL ainda precisa validar entrada? | Parametrização evita estrutura SQL maliciosa, mas não garante domínio, tamanho ou regra de negócio |
| O que acontece se Open-Meteo cair? | Timeout/JSON inválido viram WeatherUnavailable e HTTP 503; UI deixa a falha visível |
| Por que o cache? | Reduz chamadas e latência; duração de 600 s, em memória e por processo, não persiste após reinício |
| O TCP recebe tudo em um único recv? | Não; TCP é fluxo de bytes e read_frame monta até newline, com limite e timeout |
| Onde entram estruturas de dados? | Dict de cidades, listas de ocorrências, tuplas SQL, sets de chaves e deque de timestamps |
| O que o log prova? | Que determinada ação teve resultado; não identifica pessoa, não prova veracidade do relato |
| Por que não pedir nome/CPF? | Não são necessários ao objetivo demonstrado; minimização reduz exposição |
| A chave compartilhada resolve autenticação real? | Só protege a demonstração; não identifica operadores e precisa virar contas/perfis em produção |
| O que a cobertura de 95% não prova? | Não prova ausência de bugs, segurança completa ou impacto social |
| Como excluir dados? | DELETE remove o registro; logs só guardam id técnico; política de retenção real ainda precisa ser definida |
| Usou IA? | Sim, houve assistência substancial na geração; explique o que revisou/adaptou e confirme a aceitação pela professora |

## Exercícios antes da entrega

- Desenhe à mão o caminho navegador → Flask → SQL → banco e cliente → TCP → banco.
- Mude um rótulo da interface e explique por que isso não altera o valor persistido.
- Adicione uma cidade **somente depois de entender** as mudanças necessárias em allowlists Python, CHECK SQL, UI e testes.
- Desligue a internet e observe o tratamento da previsão; desligue o banco e explique 503.
- Faça uma entrada maliciosa ser rejeitada e mostre que nenhum detalhe interno aparece.
- Conte em suas palavras as limitações e uma maneira ética de validar com moradores sem coletar dados pessoais.
