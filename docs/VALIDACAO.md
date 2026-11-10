# Validação técnica e viabilidade

Execução em **10/11/2026 (UTC)**, Linux, Python 3.12.14, MySQL Community 8.4.7 em Docker, Chromium local e dependências dos requirements. Os resultados abaixo foram efetivamente observados no ambiente de desenvolvimento; não são resultados de campo.

| Verificação executada | Resultado observado | Evidência |
|---|---|---|
| Testes sem infraestrutura externa | 40 aprovados; 5 testes de integração excluídos deliberadamente | `python -m pytest -m "not integration" -q` |
| Suite com MySQL real e sockets | 45 aprovados; cobertura de 95% das instruções de `app/` | `evidencias/pytest.xml`, `evidencias/cobertura.txt` |
| Banco novo, volume separado | 45 aprovados, MySQL criado a partir do Compose/SQL entregue, porta de teste 3308 | `evidencias/instalacao-limpa.xml` |
| CRUD HTTP contra aplicação ativa | GET 200, POST 201, PUT 200, DELETE 204; escrita sem token 401; entrada maliciosa 400 | `scripts/demonstrar_api.py`, `evidencias/demonstracao-http.txt` |
| SQL parametrizado e isolamento | Payload de injeção retorna zero linhas no repositório; restrição CHECK rejeita cidade inválida; rollback remove escrita não confirmada | `tests/test_integration.py` |
| Privilégios de banco | Conta da aplicação com SELECT/INSERT/UPDATE/DELETE e sem CREATE/DROP | teste de SHOW GRANTS |
| API Open-Meteo real | HTTP 200; JSON validado com data e instante da consulta | `evidencias/open-meteo-consulta-real.json` |
| TCP real | Consulta agregada, token incorreto rejeitado, JSON/quadros inválidos rejeitados; mensagem enviada byte a byte aceita | teste com socket real e servidor em porta efêmera |
| Navegador desktop 1440 px e mobile 390 px | Criar, editar, excluir, filtrar, vazio, confirmação e estado de erro; sem erros JS observados ou overflow horizontal | `evidencias/navegador.json` e capturas PNG |
| Falha meteorológica na interface | Simulação explícita de 503, aviso visível, registros ainda exibidos | teste Playwright com interceptação da rota |
| Análise estática e sintaxe JS | Ruff aprovado; `node --check app/static/app.js` aprovado | código e configuração reproduzíveis |

Cobertura é um indicador auxiliar, não prova de ausência de defeitos. Não foram executados teste de carga, auditoria profissional, revisão de acessibilidade completa, operação em Windows/macOS ou piloto com usuários. A execução limpa confirmou o esquema e os grants depois de corrigidos os problemas encontrados na inicialização. Não foram usados mocks de banco para alegar persistência real: mocks aparecem somente nos testes unitários, separados dos testes de integração.

## Revalidação da paleta e da aba de mensagem

Em 10/11/2026, a interface passou a usar azul e roxo. A suite completa foi executada novamente com MySQL real: **45 testes aprovados, cobertura de 95% de app/**. O CRUD HTTP, a consulta TCP e a consulta real ao Open-Meteo também funcionaram; a previsão retornou HTTP 200.

O Chromium confirmou as cores efetivas do destaque roxo, do botão com gradiente azul/roxo e do indicador azul de ocorrências resolvidas. Foram validados criação, edição, exclusão, filtros, estado vazio, indisponibilidade simulada de previsão e ausência de overflow horizontal em desktop e celular.

A aba com Hebreus 13:8 começa oculta e foi aberta por **Alt + Shift + H** e por **cinco cliques no logo**, com retorno ao painel por botão e Escape. Os cinco cliques e o retorno também foram testados no viewport mobile. Não foram observados erros JavaScript. A captura está em `evidencias/aba-secreta.png`; os resultados e horário UTC estão em `evidencias/navegador.json`.

O Word do relatório foi convertido sem modificar seu conteúdo textual. Tanto sua renderização quanto o PDF mantiveram **três páginas**, com canais R/G/B iguais em todos os pixels renderizados, confirmando ausência de elementos coloridos. O gerador de PDF também foi ajustado para produzir preto e branco nas próximas execuções.

## Critérios de aceitação

- Criar e ler o mesmo id por outra conexão; atualizar status; repetir PUT sem duplicar; excluir e confirmar ausência.
- Não permitir escrita sem chave; rejeitar campos fora do domínio e payload SQL; não expor detalhes da exceção em falha de banco.
- Informar indisponibilidade de previsão sem inventar dado meteorológico e sem impedir o CRUD.
- Registrar ação/status e instante, mantendo tokens e dados do corpo fora do arquivo de auditoria.
- Demonstrar cliente TCP com framing e consulta ao MySQL.

## Validação social proposta — ainda não executada

Convidar de três a cinco pessoas adultas, voluntariamente, sem registrar nomes ou contatos, para usar apenas cenários fictícios: localizar ocorrência de um município, distinguir uma aberta de uma resolvida, identificar a fonte meteorológica e explicar por que chuva prevista não é alerta de enchente. Com autorização da professora, registrar somente contagens agregadas de sucesso e tempo aproximado. Critério proposto: pelo menos 80% concluem as tarefas sem ajuda e todas compreendem a limitação meteorológica. Se houver falha, revisar rótulos e testar novamente. Não apresentar essa meta como resultado obtido.

## Viabilidade e limitações

O piloto acadêmico roda em um computador com Python e um banco MySQL local. Não requer API paga ou LLM. A API meteorológica tem termos e limites próprios, que devem ser revistos antes de outro tipo de uso. Docker facilita a reprodução, mas exige memória, disco e internet inicial. A consulta TCP é textual e pequena, mas depende de rede e não resolve exclusão digital sozinha.

As ocorrências são simuladas e não verificadas, três municípios e três setores ilustrativos são fixos, e o único operador usa uma chave compartilhada. Não há sensores, medições hidrológicas, mapa de risco, localização precisa, integração municipal, despacho, SLA, proteção robusta contra DoS ou funcionalidade offline. O próximo passo seria validar a compreensão com moradores e pactuar governança e moderação antes de receber relatos reais.
