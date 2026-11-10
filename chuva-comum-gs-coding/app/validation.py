"""Listas permitidas: o protótipo não recebe texto livre nem dados pessoais."""
CITIES = {
    'sao-paulo': {'nome': 'São Paulo', 'latitude': -23.5505, 'longitude': -46.6333},
    'porto-alegre': {'nome': 'Porto Alegre', 'latitude': -30.0346, 'longitude': -51.2177},
    'recife': {'nome': 'Recife', 'latitude': -8.0476, 'longitude': -34.8770},
}
FIELDS = {
    'cidade': tuple(CITIES),
    'bairro': ('Setor Norte', 'Setor Central', 'Setor Sul'),
    'tipo': ('alagamento', 'bueiro_obstruido', 'via_interditada'),
    'gravidade': ('baixa', 'media', 'alta'),
    'status': ('aberta', 'em_analise', 'resolvida'),
}


class ValidationError(Exception):
    pass


def occurrence_payload(data):
    if not isinstance(data, dict) or set(data) != set(FIELDS):
        raise ValidationError('Envie somente cidade, bairro, tipo, gravidade e status.')
    for key, options in FIELDS.items():
        if not isinstance(data[key], str) or data[key] not in options:
            raise ValidationError(f'Valor inválido para {key}.')
    return {key: data[key] for key in FIELDS}


def positive_integer(value, field, maximum=2_147_483_647):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise ValidationError(f'{field} deve ser inteiro positivo.')
    if len(value) > 10 or not 1 <= int(value) <= maximum:
        raise ValidationError(f'{field} fora do intervalo permitido.')
    return int(value)


def list_params(args):
    allowed = {'cidade', 'status', 'pagina', 'limite', 'id'}
    if set(args) - allowed or any(len(args.getlist(key)) != 1 for key in args):
        raise ValidationError('Parâmetros desconhecidos ou repetidos.')
    result = {}
    for key in ('cidade', 'status'):
        if key in args:
            if args[key] not in FIELDS[key]:
                raise ValidationError(f'Filtro inválido para {key}.')
            result[key] = args[key]
    if 'id' in args:
        result['id'] = positive_integer(args['id'], 'id')
    result['pagina'] = positive_integer(args.get('pagina', '1'), 'pagina', 10000)
    result['limite'] = positive_integer(args.get('limite', '20'), 'limite', 100)
    return result
