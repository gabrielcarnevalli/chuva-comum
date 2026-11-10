# Fontes, bibliotecas e uso de IA

ChatGPT/OpenAI auxiliou apenas na concepção do projeto, em algumas partes da interface, na documentação e no levantamento de fontes. Essa assistência é declarada de forma explícita. A regra da atividade permite IA para estudo e depuração; o estudante deve confirmar com a professora a aceitação desse escopo, revisar/adaptar o material e demonstrar entendimento individual. Este documento não atesta revisão ou domínio ainda não realizados. Não devem ser declaradas autoria, entrevistas ou execução de testes que não correspondam à realidade. As fontes e dependências de terceiros utilizadas estão relacionadas a seguir

## Fontes e dependências utilizadas

| Fonte / biblioteca | Uso | Referência / licença informativa |
|---|---|---|
| FIAP Experience CitizenTech | inspiração de zeladoria colaborativa | https://experience.fiap.com.br/global-solution-citizen-tech |
| IBGE/Cemaden (2018, Censo 2010) | evidência histórica do problema | link completo no README e relatório |
| Open-Meteo | previsão aberta, requests/JSON | https://open-meteo.com/en/docs ; dados CC BY 4.0; termos da API aplicáveis |
| Flask / Werkzeug / Jinja | API e template | https://flask.palletsprojects.com/ ; BSD-3-Clause |
| MySQL Community Server | banco relacional | https://dev.mysql.com/doc/ ; GPL-2.0, termos do distribuidor |
| MySQL Connector/Python | SQL Python sem ORM | https://dev.mysql.com/doc/connector-python/en/ ; GPL-2.0 com exceções conforme distribuição |
| Requests | cliente HTTPS / JSON | https://requests.readthedocs.io/ ; Apache-2.0 |
| python-dotenv | configuração local | https://github.com/theskumar/python-dotenv ; BSD-3-Clause |
| Waitress | servidor WSGI | https://docs.pylonsproject.org/projects/waitress/ ; ZPL-2.1 |
| pytest / pytest-cov / Coverage.py | testes e cobertura | https://docs.pytest.org/ ; MIT e Apache-2.0 conforme pacote |
| Ruff | análise estática | https://docs.astral.sh/ruff/ ; MIT |
| Playwright / Chromium | teste de navegador e capturas | https://playwright.dev/python/ ; Apache-2.0 / licenças Chromium |
| ReportLab / DejaVu Sans | geração do PDF e tipografia | https://www.reportlab.com/ ; BSD / licença DejaVu |
| Docker Compose | inicialização reproduzível do MySQL | https://docs.docker.com/compose/ ; Apache-2.0, termos Docker Desktop se utilizado |

As dependências não foram copiadas para o repositório. São instaladas pelos requisitos ou pelo Docker. Não foi usado um projeto de terceiros como base, nem imagens ou templates externos de interface. Os elementos visuais foram criados com HTML/CSS/SVG no próprio projeto. Bibliotecas e dados externos mantêm suas próprias licenças; esta tabela não as substitui.

Fontes públicas consultadas em 10/11/2026. A página da FIAP foi acessada diretamente por HTTPS; a evidência histórica foi conferida na publicação do IBGE. A captura de clima real é datada e serve apenas como evidência técnica.
