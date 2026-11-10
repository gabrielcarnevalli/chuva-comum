"""Teste E2E com Chromium local. A aplicação e o MySQL devem estar ativos."""
import json
import os
from datetime import datetime, timezone
from playwright.sync_api import expect, sync_playwright

from app.config import ROOT, load_config


def main():
    config = load_config()
    evidence = ROOT / 'docs' / 'evidencias'
    errors = []
    record_id = None
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH', '/usr/bin/chromium'), headless=True,
                                             args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1440, 'height': 1080}, locale='pt-BR')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        try:
            page.goto('http://127.0.0.1:5000/', wait_until='networkidle')
            assert page.title() == 'ChuvaComum · Cuidado que começa no bairro'
            assert page.locator('#count-all').inner_text() != '—'
            theme = page.evaluate("""() => ({
                destaque: getComputedStyle(document.querySelector('.hero h1 em')).color,
                botao: getComputedStyle(document.querySelector('.primary')).backgroundImage,
                resolvida: getComputedStyle(document.querySelector('.status-resolved')).backgroundColor
            })""")
            assert theme['destaque'] == 'rgb(124, 58, 237)'
            assert 'rgb(37, 99, 235)' in theme['botao'] and 'rgb(124, 58, 237)' in theme['botao']
            assert theme['resolvida'] == 'rgb(37, 99, 235)'
            page.locator('#city').select_option('recife')
            expect(page.locator('#count-all')).not_to_have_text('—')
            page.locator('#admin-token').fill(config['ADMIN_TOKEN'])
            page.locator('#sector').select_option('Setor Sul')
            page.locator('#severity').select_option('alta')
            with page.expect_response(lambda response: '/api/ocorrencias' in response.url
                                      and response.request.method == 'POST') as create_response:
                page.locator('#submit-button').click()
            response = create_response.value
            assert response.status == 201
            record_id = response.json()['dados']['id']
            page.get_by_label(f'Editar ocorrência {record_id}', exact=True).click()
            page.locator('#record-status').select_option('resolvida')
            with page.expect_response(lambda response: response.request.method == 'PUT') as put_response:
                page.locator('#submit-button').click()
            assert put_response.value.status == 200
            page.get_by_label(f'Excluir ocorrência {record_id}', exact=True).click()
            assert page.locator('#delete-dialog').is_visible()
            with page.expect_response(lambda response: response.request.method == 'DELETE') as delete_response:
                page.locator('#confirm-delete').click()
            assert delete_response.value.status == 204
            expect(page.locator('#delete-dialog')).not_to_be_visible()
            record_id = None
            page.locator('#status-filter').select_option('resolvida')
            page.wait_for_timeout(600)
            assert page.locator('#list-message').inner_text() == 'Nenhuma ocorrência para esta seleção.'
            page.locator('#status-filter').select_option('')
            page.locator('#city').select_option('sao-paulo')
            page.locator('#admin-token').fill('')
            page.wait_for_timeout(1200)
            page.screenshot(path=str(evidence / 'painel-desktop.png'), full_page=True)
            desktop_width_ok = page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            mobile = context.new_page()
            mobile.set_viewport_size({'width': 390, 'height': 844})
            mobile.on('pageerror', lambda error: errors.append(str(error)))
            mobile.goto('http://127.0.0.1:5000/', wait_until='networkidle')
            mobile.screenshot(path=str(evidence / 'painel-mobile.png'), full_page=True)
            mobile_width_ok = mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert desktop_width_ok and mobile_width_ok
            # A aba começa oculta; testar teclado, fechamento e cinco cliques em ambos os tamanhos.
            expect(page.locator('#secret-nav')).to_be_hidden()
            expect(page.locator('#secret-panel')).to_be_hidden()
            page.keyboard.press('Alt+Shift+h')
            expect(page.locator('#secret-panel')).to_be_visible()
            expect(page.locator('#community-content')).to_be_hidden()
            expect(page.get_by_text('Jesus Cristo é o mesmo ontem, hoje e eternamente.', exact=True)).to_be_visible()
            expect(page.get_by_text('Hebreus 13:8', exact=True)).to_be_visible()
            page.screenshot(path=str(evidence / 'aba-secreta.png'), full_page=True)
            page.keyboard.press('Escape')
            expect(page.locator('#community-content')).to_be_visible()
            for _ in range(5):
                page.locator('#brand-home').click()
            expect(page.locator('#secret-panel')).to_be_visible()
            page.locator('#close-secret').click()
            expect(page.locator('#community-content')).to_be_visible()
            for _ in range(5):
                mobile.locator('#brand-home').click()
            expect(mobile.locator('#secret-panel')).to_be_visible()
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
            mobile.locator('#close-secret').click()
            expect(mobile.locator('#community-content')).to_be_visible()
            assert not errors
            # Falha de previsão é uma simulação explícita para exercitar o estado de erro.
            page.route('**/api/clima?**', lambda route: route.fulfill(
                status=503, content_type='application/json', body='{"erro":"Previsão indisponível."}'))
            page.locator('#city').select_option('porto-alegre')
            page.get_by_text('Previsão indisponível', exact=True).wait_for()
            assert page.locator('#retry-weather').is_visible()
            assert page.locator('#records .record').count() >= 1
            result = {'crud_real_no_navegador': 'aprovado', 'filtro_e_estado_vazio': 'aprovado',
                      'previsao_indisponivel_simulada': 'aprovado', 'erros_javascript': errors,
                      'desktop_sem_overflow': desktop_width_ok, 'mobile_sem_overflow': mobile_width_ok,
                      'paleta': 'azul e roxo', 'cores_observadas': theme,
                      'aba_hebreus_13_8_teclado_desktop_mobile': 'aprovado',
                      'executado_em_utc': datetime.now(timezone.utc).isoformat()}
            (evidence / 'navegador.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False))
        finally:
            if record_id is not None:
                # Limpa somente o registro criado por este teste.
                context.request.delete(f'http://127.0.0.1:5000/api/ocorrencias/{record_id}',
                                       headers={'Authorization': 'Bearer ' + config['ADMIN_TOKEN']})
            browser.close()


if __name__ == '__main__':
    main()
