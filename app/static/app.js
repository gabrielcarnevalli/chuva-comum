'use strict';
const $ = (id) => document.getElementById(id);
const labels = {alagamento:'Alagamento', bueiro_obstruido:'Bueiro obstruído', via_interditada:'Via interditada', baixa:'Baixa', media:'Média', alta:'Alta', aberta:'Aberta', em_analise:'Em análise', resolvida:'Resolvida'};
let page = 1, records = [], listVersion = 0, weatherVersion = 0, deleteId = null, busy = false;
const limit = 5;

async function api(path, options = {}) {
  let response;
  try { response = await fetch(path, {...options, signal: AbortSignal.timeout(15000)}); }
  catch { throw new Error('Não foi possível conectar. Verifique a conexão e tente novamente.'); }
  if (response.status === 204) return null;
  let body;
  try { body = await response.json(); }
  catch { throw new Error('Resposta indisponível. Tente novamente.'); }
  if (!response.ok) throw new Error(body.erro || 'Não foi possível concluir a operação.');
  return body;
}
function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}
function auth() {
  const token = $('admin-token').value.trim();
  if (token.length < 32) throw new Error('Informe uma chave de edição válida para continuar.');
  return {Authorization:`Bearer ${token}`, 'Content-Type':'application/json'};
}
function setBusy(value) {
  busy = value;
  $('submit-button').disabled = value;
  $('confirm-delete').disabled = value;
  $('city').disabled = value;
}
function renderRecords() {
  $('records').replaceChildren();
  for (const item of records) {
    const row = node('article', 'record');
    const main = node('div');
    const title = node('h4', 'record-type');
    const symbol = node('span', 'record-symbol', '◉');
    symbol.setAttribute('aria-hidden', 'true');
    title.append(symbol, document.createTextNode(labels[item.tipo]));
    const date = new Date(item.criado_em).toLocaleDateString('pt-BR');
    main.append(title, node('p', 'record-meta', `${item.bairro} · Registro em ${date}`));
    const badges = node('div', 'record-badges');
    badges.append(node('span', `pill ${item.status}`, labels[item.status]), node('span', `pill ${item.gravidade}`, `Gravidade ${labels[item.gravidade].toLowerCase()}`));
    main.append(badges);
    const side = node('div', 'record-side');
    side.append(node('span', 'record-id', `#${String(item.id).padStart(3,'0')}`));
    const actions = node('div', 'record-actions');
    const edit = node('button', '', 'Editar');
    edit.type = 'button'; edit.setAttribute('aria-label', `Editar ocorrência ${item.id}`);
    edit.addEventListener('click', () => {if (!busy) startEdit(item);});
    const remove = node('button', 'delete-button', 'Excluir');
    remove.type = 'button'; remove.setAttribute('aria-label', `Excluir ocorrência ${item.id}`);
    remove.addEventListener('click', () => {
      if (busy) return;
      try {auth();} catch(error) {$('form-message').textContent=error.message; $('admin-token').focus(); return;}
      deleteId = item.id; $('delete-dialog').showModal();
    });
    actions.append(edit, remove); side.append(actions); row.append(main, side); $('records').append(row);
  }
}
async function loadRecords() {
  const version = ++listVersion;
  const city = $('city').value;
  const params = new URLSearchParams({cidade:city, pagina:page, limite:limit});
  if ($('status-filter').value) params.set('status', $('status-filter').value);
  $('list-message').textContent = 'Carregando ocorrências…';
  try {
    const base = `/api/ocorrencias?cidade=${encodeURIComponent(city)}&limite=1`;
    const [data, all, open, done] = await Promise.all([
      api(`/api/ocorrencias?${params}`), api(base), api(`${base}&status=aberta`), api(`${base}&status=resolvida`)
    ]);
    if (version !== listVersion) return;
    if (page > 1 && !data.dados.length) {page--; return loadRecords();}
    records = data.dados;
    $('count-all').textContent=all.total; $('count-open').textContent=open.total; $('count-done').textContent=done.total;
    $('list-message').textContent = records.length ? '' : 'Nenhuma ocorrência para esta seleção.';
    $('page-label').textContent=`Página ${page} de ${Math.max(1,Math.ceil(data.total/limit))}`;
    $('previous').disabled=page === 1; $('next').disabled=page*limit >= data.total;
    renderRecords();
  } catch(error) {
    if (version !== listVersion) return;
    records=[]; renderRecords(); $('list-message').textContent=error.message;
    for (const id of ['count-all','count-open','count-done']) $(id).textContent='—';
    $('previous').disabled=true; $('next').disabled=true;
  }
}
async function loadWeather() {
  const version=++weatherVersion;
  $('weather-main').textContent='Consultando previsão…'; $('retry-weather').hidden=true;
  $('weather-detail').textContent='Open-Meteo · informação municipal';
  try {
    const {dados} = await api(`/api/clima?cidade=${encodeURIComponent($('city').value)}`);
    if (version !== weatherVersion) return;
    $('weather-main').textContent=`${new Intl.NumberFormat('pt-BR').format(dados.precipitacao_mm)} mm previstos`;
    const day = dados.data.split('-').reverse().join('/');
    $('weather-detail').textContent=`${day} · ${dados.probabilidade_chuva}% de chance de chuva · ${dados.cache ? 'cache de até 10 min' : 'consulta atual'}`;
  } catch(error) {
    if (version !== weatherVersion) return;
    $('weather-main').textContent='Previsão indisponível';
    $('weather-detail').textContent='Consulte os canais oficiais. Os registros seguem disponíveis.';
    $('retry-weather').hidden=false;
  }
}
function resetForm() {
  $('edit-id').value=''; $('form-title').textContent='Registrar ocorrência';
  $('submit-button').replaceChildren(document.createTextNode('Registrar ocorrência →'));
  $('cancel-edit').hidden=true;
  $('sector').value='Setor Norte'; $('type').value='alagamento';
  $('severity').value='baixa'; $('record-status').value='aberta';
}
function startEdit(item) {
  $('edit-id').value=item.id; $('sector').value=item.bairro; $('type').value=item.tipo;
  $('severity').value=item.gravidade; $('record-status').value=item.status;
  $('form-title').textContent=`Editar ocorrência #${item.id}`;
  $('submit-button').textContent='Salvar alterações →'; $('cancel-edit').hidden=false;
  $('form-message').textContent='Altere os campos e salve para atualizar o registro.';
  $('form-title').scrollIntoView({block:'center'}); $('sector').focus({preventScroll:true});
}
$('occurrence-form').addEventListener('submit', async (event) => {
  event.preventDefault(); if (busy) return;
  const id=$('edit-id').value;
  try {
    const headers=auth(); setBusy(true); $('form-message').textContent='Salvando…';
    await api(`/api/ocorrencias${id ? '/'+id : ''}`, {method:id?'PUT':'POST', headers,
      body:JSON.stringify({cidade:$('city').value, bairro:$('sector').value, tipo:$('type').value, gravidade:$('severity').value, status:$('record-status').value})});
    resetForm(); $('form-message').textContent=id?'Alterações salvas.':'Ocorrência fictícia registrada.';
    page=1; await loadRecords();
  } catch(error) {$('form-message').textContent=error.message;}
  finally {setBusy(false);}
});
$('confirm-delete').addEventListener('click', async () => {
  if (busy || deleteId === null) return;
  try {
    const headers=auth(); setBusy(true);
    await api(`/api/ocorrencias/${deleteId}`, {method:'DELETE', headers});
    if ($('edit-id').value === String(deleteId)) resetForm();
    $('form-message').textContent='Ocorrência excluída.';
    await loadRecords();
  } catch(error) {$('form-message').textContent=error.message;}
  finally {$('delete-dialog').close(); deleteId=null; setBusy(false);}
});
$('cancel-delete').addEventListener('click', () => {if (!busy) {$('delete-dialog').close(); deleteId=null;}});
$('delete-dialog').addEventListener('cancel', (event) => {if (busy) event.preventDefault();});
$('cancel-edit').addEventListener('click', () => {if (!busy) {resetForm(); $('form-message').textContent='';}});
$('city').addEventListener('change', () => {page=1; resetForm(); $('form-message').textContent=''; loadRecords(); loadWeather();});
$('status-filter').addEventListener('change', () => {page=1; loadRecords();});
$('refresh').addEventListener('click', loadRecords);
$('retry-weather').addEventListener('click', loadWeather);
$('previous').addEventListener('click', () => {if (page>1) {page--; loadRecords();}});
$('next').addEventListener('click', () => {page++; loadRecords();});
window.addEventListener('pagehide', () => {$('admin-token').value='';});

// Aba de mensagem: cinco cliques seguidos no logo ou Alt+Shift+H.
let brandClicks = 0, lastBrandClick = 0;
function showCommunityPanel() {
  $('community-content').hidden=false;
  $('secret-panel').hidden=true;
  $('secret-nav').classList.remove('active');
  $('panel-nav').classList.add('active');
}
function showSecretPanel() {
  if (busy || $('delete-dialog').open) return;
  $('secret-nav').hidden=false;
  $('community-content').hidden=true;
  $('secret-panel').hidden=false;
  $('panel-nav').classList.remove('active');
  $('secret-nav').classList.add('active');
  $('secret-title').focus({preventScroll:true});
  window.scrollTo({top:0, behavior:'instant'});
}
$('brand-home').addEventListener('click', (event) => {
  event.preventDefault();
  const now=Date.now();
  brandClicks = now-lastBrandClick > 2500 ? 1 : brandClicks+1;
  lastBrandClick=now;
  if (brandClicks >= 5) {brandClicks=0; showSecretPanel();}
  else {showCommunityPanel(); window.scrollTo({top:0, behavior:'instant'});}
});
$('secret-nav').addEventListener('click', (event) => {event.preventDefault(); showSecretPanel();});
$('panel-nav').addEventListener('click', showCommunityPanel);
$('about-nav').addEventListener('click', showCommunityPanel);
$('close-secret').addEventListener('click', () => {showCommunityPanel(); $('panel-nav').focus();});
document.addEventListener('keydown', (event) => {
  if (event.altKey && event.shiftKey && event.code === 'KeyH') {
    event.preventDefault(); showSecretPanel();
  } else if (event.key === 'Escape' && !$('secret-panel').hidden) {
    showCommunityPanel(); $('panel-nav').focus();
  }
});
loadRecords(); loadWeather();
