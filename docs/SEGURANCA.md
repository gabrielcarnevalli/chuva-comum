# Segurança, privacidade e limites

## Três ameaças e mitigações

| Ameaça / impacto | Mitigação implementada | Evidência e limite |
|---|---|---|
| **1. Injeção SQL:** leitura/alteração indevida ou destruição de dados por entrada maliciosa | SQL constante e parâmetros `%s` em todas as entradas; colunas de filtro fixas; validação de tipo e allowlists; CHECK/ENUM no banco; usuário sem DDL | Teste direto do repositório com `' OR 1=1 --` retorna zero linhas. Teste HTTP rejeita o filtro com 400. Privilégios conferidos com SHOW GRANTS. |
| **2. Edição não autorizada e vazamento de credenciais:** falsificação de status/exclusão | Bearer obrigatório nas escritas, comparação com `hmac.compare_digest`, tokens aleatórios separados HTTP/TCP em `.env`, `.gitignore`, nenhum token no HTML, log, URL ou armazenamento web; mesma origem sem CORS | Testes sem token retornam 401; auditoria não contém a credencial. Uma chave compartilhada não identifica operadores: comprometimento exige rotação e uso real requer contas/perfis e TLS. |
| **3. Abuso ou indisponibilidade de serviço:** excesso de pedidos, quadros TCP grandes e falha de provedor | 120 pedidos/min por IP/processo, corpo HTTP 4 KB, lista até 100 itens; cache meteorológico de dez minutos, timeouts e 503 explícito; TCP local com 1024 bytes/2 s; credencial própria | Testes de 429, 413, timeout externo e quadro excessivo. Interface mostra previsão indisponível e preserva registros. Limite em memória e servidor TCP sequencial não resolvem DoS distribuído. |

## Controles complementares

Não há campos de texto livre; HTML usa `textContent` para dados retornados e Jinja faz escape do template. Política CSP limita scripts, estilos e conexões à própria origem, sem `unsafe-inline`/`unsafe-eval`. `nosniff`, proteção a frames e `no-referrer` complementam a resposta. A interface não usa cookies de autenticação: a chave deve ser enviada explicitamente em um header, reduzindo exposição a CSRF clássico por formulário entre origens. Sem CORS permissivo, outro site não obtém autorização automaticamente.

O endpoint externo é fixo, aceita apenas municípios cadastrados e rejeita URLs fornecidas pelo cliente, reduzindo SSRF. O cliente requests mantém verificação TLS; não há `verify=False`. MySQL usa conta DML própria; root serve apenas à inicialização no Docker. Debug não é ativado. Banco, HTTP e TCP escutam em localhost na configuração de demonstração.

## LGPD: coleta mínima por desenho

- Registros exclusivamente sintéticos; coordenadas meteorológicas são públicas e municipais. O sistema não solicita nome, CPF, e-mail, telefone, foto, endereço residencial ou GPS individual.
- Formulário e API recebem somente categorias predefinidas. Não há campo de relato que permita inserir dados pessoais acidentalmente.
- Auditoria guarda data/hora UTC, ação, resultado/status HTTP e eventualmente id técnico; não guarda corpo, IP, query string nem cabeçalhos.
- O controle de requisições utiliza o IP transitoriamente na memória do processo, com até 2048 chaves; não o registra no arquivo. Isso ainda exige transparência e revisão se o serviço for público.
- O cache externo guarda somente previsão municipal. Nenhuma ocorrência é enviada à Open-Meteo.
- Logs têm rotação por tamanho (um arquivo de até 1 MB mais três backups por handler). Isso não equivale a política temporal de retenção. Em uma demonstração descartável, o responsável pode apagar logs após a avaliação; para produção, definir prazo, controle de acesso e descarte.
- A minimização se orienta pelos princípios de finalidade/necessidade da LGPD; não é alegação de certificação ou adequação jurídica completa.

## O que falta para implantação pública

Contas individuais, papéis e revogação, TLS e autenticação de banco/servidor, moderação e verificação dos relatos, consentimento e política de privacidade conforme o tratamento efetivo, monitoramento e backups, limitação distribuída, acesso aos logs, integração oficial, estratégia de retenção e atendimento a direitos. Se houver proxy, o IP do visitante deve ser tratado com configuração confiável; o protótipo não confia em X-Forwarded-For enviado pelo usuário.
