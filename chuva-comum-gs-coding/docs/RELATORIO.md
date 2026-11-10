# ChuvaComum
## Cuidado que começa no bairro

**Global Solution | Coding for Security | CitizenTech**

**Estudante:** {{NOME}} | **RM:** {{RM}} | **Turma:** {{TURMA}}

### 1. Problema, cidadão e evidência

O cidadão considerado é o morador de região urbana sujeita a alagamentos que precisa acompanhar problemas coletivos e seu andamento. A hipótese é que um painel simples pode reunir registros dispersos e tornar visível o que está aberto, em análise ou resolvido. No protótipo, a consulta é pública e um representante comunitário simulado opera as alterações com chave local.

Como evidência pública, o estudo IBGE/Cemaden divulgado em 2018 identificou **8.270.127 moradores em áreas de risco em 872 municípios**, com base no Censo 2010 [2]. O dado comprova exposição histórica, não dimensiona a situação atual nem comprova demanda pela interface. Não foram realizadas entrevistas ou validação com moradores.

A inspiração é a proposta de **zeladoria colaborativa** do Experience FIAP CitizenTech, para identificar e acompanhar problemas dos espaços públicos [1]. A solução delimita esse tema a alagamentos, bueiros obstruídos e vias interditadas.

### 2. ODS e contribuição pretendida

**ODS 11 — Cidades e comunidades sustentáveis:** organização participativa de informações locais, associada às metas 11.3 e 11.5. **ODS 13 — Ação climática:** apoio à preparação e adaptação local, associado à meta 13.1 [4]. A contribuição é informacional; redução de danos ou de vítimas não foi medida.

### 3. Solução e escopo funcional

A interface HTML/CSS/JavaScript consome uma API Flask. Permite listar, criar, editar e excluir registros fictícios, filtrar município/status, acompanhar contagens e consultar previsão municipal de chuva. São Paulo, Porto Alegre e Recife compõem o recorte. “Setor Norte”, “Setor Central” e “Setor Sul” são regiões ilustrativas, não bairros cadastrados.

Os quatro endpoints CRUD são **GET/POST /api/ocorrencias** e **PUT/DELETE /api/ocorrencias/{id}**: sucesso retorna 200, 201 com Location, 200 e 204 sem corpo, respectivamente. GET auxiliar /api/clima consulta a fonte externa. Entradas inválidas recebem 400; credencial inválida, 401; registro inexistente em alteração/exclusão, 404; indisponibilidade, 503.

A previsão de chuva **não prevê enchentes**, não determina rotas seguras e não substitui a Defesa Civil. O sistema não despacha equipes nem envia alertas oficiais. O painel indica claramente o caráter fictício e os canais 199/193 para emergências.

<!-- PAGEBREAK -->

## Arquitetura, dados e segurança

### 4. Arquitetura e integração externa

**Web:** navegador -> Flask/Waitress -> validação -> repositório Python -> MySQL 8.4. **Meteorologia:** Flask -> requests/HTTPS -> Open-Meteo -> JSON validado -> painel. **Sockets:** cliente TCP -> servidor TCP local -> repositório -> MySQL. Flask e TCP registram data/hora UTC, ação e resultado em arquivo com rotação.

Não há ORM. O repositório usa MySQL Connector/Python e consultas parametrizadas com %s; o contexto de conexão faz commit/rollback e fecha recursos. O serviço externo usa coordenadas municipais fixas, timeout de conexão/leitura e cache de dez minutos. Rejeita JSON inválido e mostra falha explícita, sem criar previsões fictícias [3].

O módulo escolhido é **sockets TCP**, sem LLM. Troca JSON UTF-8 terminado por newline, com limite de 1024 bytes, timeout de 2 s e credencial própria. O servidor agrega quantidades por status e trata mensagens fragmentadas. Escuta somente em loopback; é uma demonstração local, com rede disponível, não uma solução offline.

### 5. Modelo de dados

Uma única entidade representa o escopo: **ocorrencias**. Não é necessário cadastrar cidadãos.

| Campo | Tipo e regra |
| id | INT UNSIGNED, chave primária e auto incremento |
| cidade / bairro | VARCHAR(30), NOT NULL, CHECK com opções permitidas |
| tipo | ENUM: alagamento, bueiro_obstruido, via_interditada |
| gravidade / status | ENUM: baixa/media/alta; aberta/em_analise/resolvida |
| criado_em / atualizado_em | TIMESTAMP(6), gerados/atualizados pelo banco, UTC |

Há índice (cidade, status), paginação até 100 itens e usuário do banco restrito a SELECT/INSERT/UPDATE/DELETE. As listas permitidas também são validadas no Python. Dicts, listas, tuplas, sets e deque organizam configuração, registros, parâmetros e controle de acesso.

### 6. Três ameaças e mitigação

**1 — Injeção SQL:** comandos constantes e parâmetros separados, allowlists de campos/valores e restrições no banco. Testes HTTP e de repositório exercitam payload de injeção. **2 — Edição indevida/vazamento de chave:** Bearer nas escritas, comparação segura, segredos aleatórios em .env ignorado pelo Git, tokens HTTP/TCP distintos, sem persistência da chave na interface ou nos logs. **3 — Abuso/indisponibilidade:** limite de 120 requisições/min por IP/processo, corpo até 4 KB, paginação, timeout/cache externo e limite de quadro TCP. São controles de protótipo, sem garantia contra ataques distribuídos.

À luz da **LGPD** [5], não se coletam nomes, CPF, contatos, fotos, endereço ou GPS pessoal. Campos têm opções fixas e os dados são fictícios ou abertos. O IP é usado transitoriamente em memória para limitar acesso; o log não guarda IP, corpo ou credenciais. CSP, textContent e erros genéricos complementam a proteção. Um uso público exigiria política de retenção, contas individuais, TLS e governança.

<!-- PAGEBREAK -->

## Validação, limites e transparência

### 7. Validação efetivamente executada

Em **10/11/2026**, com Python 3.12.14 e MySQL 8.4.7 real, **45 testes passaram**, com **95% de cobertura das instruções de app/**. Abrangeram CRUD/persistência em outra conexão, PUT repetido, rollback, SQL injection, CHECK, privilégios mínimos, erros sem detalhes internos, autenticação, 413/429, cache e falha externa, além de TCP real com mensagem fragmentada e quadros inválidos.

Uma instalação em **volume MySQL novo e separado** também passou os 45 testes, confirmando a inicialização do esquema. A API Open-Meteo real retornou 200; a resposta datada foi preservada. Em Chromium, foram exercitados criação, edição, exclusão, filtros, estado vazio e falha meteorológica simulada. Capturas desktop (1440 px) e mobile (390 px) não apresentaram overflow horizontal; não foram observados erros JavaScript. Ruff e verificação de sintaxe JS passaram. Evidências reproduzíveis acompanham o ZIP em docs/evidencias.

**Validação social proposta, não realizada:** três a cinco voluntários usando apenas cenários fictícios, sem nomes/contatos, para localizar e interpretar ocorrências e distinguir previsão de alerta. Meta proposta: 80% de conclusão sem ajuda e compreensão unânime da limitação meteorológica. Resultados reais precisariam orientar a próxima versão.

### 8. Viabilidade, limitações e recursos adicionais

O protótipo roda em um computador com Python e MySQL via Docker, sem API paga ou LLM. Depende de internet para a previsão e está sujeito aos termos do provedor. Só cobre três cidades/setores fictícios; não verifica relatos, não mede rios, não integra órgãos públicos e não oferece operação offline. A chave compartilhada não identifica operadores, e o limite em memória não equivale a proteção distribuída. Não houve teste de carga ou piloto comunitário.

**Adicionais usados e justificativa (possível bônus):** Docker Compose reproduz banco/esquema; pytest/cobertura e Playwright geram evidência verificável; Waitress evita o servidor de desenvolvimento; CSP e controle de acesso reduzem superfícies de abuso. Esses recursos apoiam a confiabilidade da demonstração, sem alegar prontidão para produção.

### 9. Autoria e uso de IA

**ChatGPT/OpenAI auxiliou apenas na concepção do projeto, em algumas partes da interface, na documentação e no levantamento de fontes. Essa assistência é declarada de forma explícita. A regra da disciplina menciona IA para estudo e depuração: o estudante deve confirmar a aceitação desse escopo, revisar/adaptar o material e demonstrar domínio individual. Este relatório não atesta revisão ou domínio ainda não realizados. Dependências e fontes de terceiros constam em docs/CREDITOS.md.

### Referências (acesso em 10/11/2026)

[1] FIAP. Global Solution CitizenTech. https://experience.fiap.com.br/global-solution-citizen-tech

[2] IBGE. Em 2010, Brasil tinha 8,3 milhões de pessoas morando em áreas com risco de desastres naturais. 28/06/2018. [Publicação original (release 21565)](https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/21565-em-2010-brasil-tinha-8-3-milhoes-de-pessoas-morando-em-areas-com-risco-de-desastres-naturais).

[3] Open-Meteo. Weather Forecast API. https://open-meteo.com/en/docs (dados CC BY 4.0).

[4] ONU Brasil. ODS 11 e 13. https://brasil.un.org/pt-br/sdgs/11 e /13.

[5] Brasil. Lei 13.709/2018 (LGPD), art. 6º. [Texto oficial — Portal Planalto](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm).
