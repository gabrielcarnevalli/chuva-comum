# Contrato da API

Base local: `http://127.0.0.1:5000`. JSON UTF-8. GET é público; POST, PUT e DELETE exigem `Authorization: Bearer <ADMIN_TOKEN>`. Token inválido/ausente: 401 com `WWW-Authenticate`. Não envie credenciais na URL. Limite de corpo: 4 KB; limite de acesso: 120 requisições por minuto por IP/processo. Resposta 429 tem `Retry-After: 60`.

| Método e caminho | Resultado |
|---|---|
| GET `/api/ocorrencias` | 200, `dados`, `total`, `pagina`, `limite` |
| POST `/api/ocorrencias` | 201, `dados` com registro criado; `Location: /api/ocorrencias?id=<id>` |
| PUT `/api/ocorrencias/<id>` | 200, `dados` com substituição dos cinco campos mutáveis |
| DELETE `/api/ocorrencias/<id>` | 204, sem corpo |
| GET `/api/clima?cidade=<slug>` | 200, previsão Open-Meteo; 503 se indisponível |

## Listar e buscar

GET aceita somente `cidade`, `status`, `id`, `pagina` (1–10000), `limite` (1–100, padrão 20). Parâmetros repetidos, desconhecidos e fora das listas permitidas geram 400. A lista é ordenada por id decrescente. `?id=123` consulta um registro pela mesma rota de listagem; inexistente retorna `dados: []`, `total: 0`, HTTP 200. PUT/DELETE de um id inexistente retornam 404.

```bash
curl "http://127.0.0.1:5000/api/ocorrencias?cidade=sao-paulo&pagina=1&limite=5"
curl "http://127.0.0.1:5000/api/clima?cidade=sao-paulo"
```

## Criar / atualizar

Exatamente cinco campos, todos obrigatórios e todos strings de listas permitidas:

```json
{
  "cidade": "sao-paulo",
  "bairro": "Setor Norte",
  "tipo": "alagamento",
  "gravidade": "alta",
  "status": "aberta"
}
```

Valores permitidos:

- cidade: `sao-paulo`, `porto-alegre`, `recife`.
- bairro: `Setor Norte`, `Setor Central`, `Setor Sul` (regiões fictícias).
- tipo: `alagamento`, `bueiro_obstruido`, `via_interditada`.
- gravidade: `baixa`, `media`, `alta`.
- status: `aberta`, `em_analise`, `resolvida`.

IDs e datas são gerados pelo banco. Não há PATCH. PUT substitui integralmente os cinco campos mutáveis; repetir o mesmo PUT mantém o estado e retorna 200. POST/PUT rejeitam query strings; DELETE rejeita query strings e corpo.

Use a interface ou `python -m scripts.demonstrar_api` para demonstrar as escritas sem colocar a chave no histórico do shell. Exemplo Python:

```python
from dotenv import load_dotenv
import os
import requests

load_dotenv()
resposta = requests.post(
    'http://127.0.0.1:5000/api/ocorrencias',
    headers={'Authorization': 'Bearer ' + os.environ['ADMIN_TOKEN']},
    json={'cidade': 'sao-paulo', 'bairro': 'Setor Norte', 'tipo': 'alagamento',
          'gravidade': 'alta', 'status': 'aberta'},
    timeout=10,
)
print(resposta.status_code, resposta.json())  # nunca imprimir o header
```

## Erros

| HTTP | Quando |
|---|---|
| 400 | JSON malformado, campos extras/ausentes, tipos/valores/filtros/ids inválidos |
| 401 | escrita sem chave válida |
| 404 | rota inexistente ou registro inexistente em PUT/DELETE |
| 405 | método não suportado; header Allow |
| 413 | corpo acima de 4 KB |
| 415 | POST/PUT sem Content-Type application/json |
| 429 | limite por IP/processo excedido |
| 503 | falha de banco ou previsão externa |
| 500 | falha inesperada, sem detalhes internos |

Erros tratados no Flask têm `{"erro":"Mensagem pública."}`. O servidor HTTP pode rejeitar requisições excedentes antes de chegarem ao Flask. Respostas não expõem SQL, traceback, senha ou host interno.

## Previsão

O servidor consulta `https://api.open-meteo.com/v1/forecast` com coordenadas centrais fixas, `daily=precipitation_sum,precipitation_probability_max`, `forecast_days=1`, `timezone=America/Sao_Paulo`. Valida data, unidades e limites numéricos. JSON público inclui data, milímetros previstos, probabilidade de chuva, instante de consulta UTC, fonte, aviso e indicação de cache. Cache por município por dez minutos, por processo. Falhas não devolvem clima fictício ou uma previsão antiga como atual.

## Protocolo TCP

Porta padrão 5050, somente loopback, sem TLS. Essa restrição é imposta no servidor e no cliente. Token diferente do HTTP. Mensagem UTF-8 com JSON e `\n`, no máximo 1024 bytes incluindo delimitador, timeout de leitura de 2 segundos, um pedido por conexão:

```json
{"acao":"resumo","token":"valor-local-de-TCP_TOKEN"}
```

Resposta de exemplo **ilustrativa**:

```json
{"dados":{"aberta":2,"em_analise":2,"resolvida":1}}
```

O resumo agrega todas as cidades. Pacotes TCP podem chegar fragmentados, por isso `read_frame` acumula bytes até o delimitador. Comando incorreto, token inválido, UTF-8/JSON inválido ou quadro excessivo recebe erro sem conteúdo interno. O servidor é sequencial, próprio para a demonstração local; não tem garantia de disponibilidade sob ataque e não deve ser exposto a redes públicas.
