(() => {
  'use strict';

  const API_ROOT = 'https://homebrew.page/api/v1';
  const INDEX_URL = `${API_ROOT}/index.json`;
  const STORAGE_QUEUE = 'ps5-atlas-download-queue-v1';
  const STORAGE_SOURCES = 'ps5-atlas-custom-sources-v1';
  const STORAGE_CATALOG_SEQUENCE = 'ps5-atlas-homebrew-catalog-sequence-v1';
  // Public Ed25519 signing keys published in homebrew.page's API documentation.
  const CATALOG_PUBLIC_KEYS = [
    '87391bf1698ecef101bf5e29dc8585ee5947d571e19470de7411c5d3b137b5cf',
    '509bcfab7edfb4e5ed23639488517c6ef2657c13b6b7f2bf699c8989d9b0dd7b'
  ];
  const MAX_BROWSER_DOWNLOAD = 120 * 1024 * 1024;
  const ACCEPTED_DOWNLOAD_HOSTS = new Set([
    'github.com', 'objects.githubusercontent.com', 'release-assets.githubusercontent.com'
  ]);
  const $ = (selector, root = document) => root.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const fmtSize = bytes => {
    if (bytes === null || bytes === undefined || bytes === '' || !Number.isFinite(Number(bytes)) || Number(bytes) < 0) return '—';
    const units = ['B', 'KB', 'MB', 'GB']; let n = Number(bytes), i = 0;
    while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
    return `${n.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
  };
  const dateLabel = value => {
    if (!value) return '—';
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleDateString(language === 'pt' ? 'pt-PT' : 'en-GB');
  };
  let language = (() => { try { return localStorage.getItem('ps5-atlas-language') === 'en' ? 'en' : 'pt'; } catch { return 'pt'; } })();
  const T = {
    pt: {
      loading:'A verificar assinatura e consultar o catálogo homebrew.page…', loaded:'Assinatura e hash do catálogo confirmados', unavailable:'Não foi possível carregar o catálogo em direto. Podes abrir a fonte oficial ou tentar novamente.',
      catalogCount:n=>`${n} aplicações disponíveis no catálogo`, noApps:'Não foram encontradas aplicações para esta pesquisa.', searchPlaceholder:'Pesquisar aplicação, autor ou Title ID…',
      refresh:'Atualizar catálogo ↻', catalog:'Catálogo comunitário de homebrew', detail:'Detalhes', addQueue:'Adicionar à fila', release:'Release oficial ↗', repo:'Código-fonte ↗',
      titleId:'Title ID', author:'Autor', version:'Versão', license:'Licença', format:'Formato', size:'Tamanho', released:'Publicada', description:'Descrição', releaseNotes:'Notas da release', detailsLoading:'A verificar e consultar os detalhes…', detailsUnavailable:'Não foi possível obter os detalhes assinados. Abre a página do catálogo ou tenta novamente.', safety:'Análise informativa',
      safetyStays:'Não foi encontrada saída da sandbox na análise publicada', safetyLeaves:'O pacote declara/foi detetado como capaz de sair da sandbox', safetyUnclear:'Análise de segurança inconclusiva', safetyUnknown:'Sem dados de análise',
      queueEmpty:'A fila está vazia.', queueQueued:'Na fila', queueDownloading:'A transferir', queuePaused:'Em pausa', queueVerified:'Hash confirmado — pronto a guardar', queueSaved:'Transferido e guardado pelo utilizador', queueError:'Falhou', queueCancelled:'Cancelado', queueExternal:'Transferência direta indisponível; abre a release oficial.',
      startQueue:'Iniciar fila', pause:'Pausa', resume:'Retomar', cancel:'Cancelar', saveFile:'Guardar ficheiro verificado', openRelease:'Abrir release oficial ↗', clearQueue:'Limpar', added:'Adicionado à fila.',
      checksumMissing:'Não há SHA-256 publicado; só está disponível a página oficial.', checksumInvalid:'O URL do ficheiro não está num domínio de release aprovado.', tooLarge:'O ficheiro excede o limite de 120 MB da transferência no navegador. Usa a release oficial.',
      checksumMismatch:'O SHA-256 não corresponde ao catálogo. O ficheiro foi rejeitado.', checksumPassed:'SHA-256 confirmado.', browserNoCors:'O fornecedor não permite transferência direta a partir deste site (CORS). Abre a release oficial.',
      providersTitle:'Outras ferramentas e lojas oficiais', providersIntro:'Páginas oficiais dos próprios projetos. O Atlas não importa os catálogos de jogos dessas aplicações.',
      sourceHomebrew:'Catálogo comunitário', sourceTool:'Projeto homebrew', sourceProvider:'Fornecedor externo (manual)', openProvider:'Abrir página do fornecedor ↗', checkRelease:'Consultar última release',
      orbitDescription:'Loja homebrew para PS5; consulta o projeto e as suas releases oficiais.', spectrumDescription:'Aplicação de biblioteca/loja da comunidade; consulta o projeto e as suas releases oficiais.',
      vikingDescription:'Sem conector automático: abre a página do fornecedor e segue os passos do site. O Atlas não contorna CAPTCHA, login nem links temporários.',
      homebrewPageDescription:'Catálogo comunitário de aplicações PS5 com páginas de projeto, releases e hashes publicados.', ps5LibraryDescription:'Projeto de biblioteca autoalojada para homebrew e conteúdos a que o operador tem autorização de acesso; o catálogo/servidor é gerido pelo próprio utilizador.',
      loadingRelease:'A consultar release…', latestRelease:'Última release', noAssets:'A release não tem ficheiros anexados.', assetHash:'Hash SHA-256 publicado', assetNoHash:'Sem hash consultável na API — abre a release para verificar.',
      customTitle:'Fontes personalizadas', customIntro:'Guarda páginas de projetos ou releases que tens autorização para usar. As fontes ficam no teu navegador e não são publicadas.',
      customName:'Nome da fonte', customUrl:'URL da página do projeto/release', customNamePlaceholder:'O meu projeto autorizado', customUrlPlaceholder:'https://github.com/autor/projeto',
      customConsent:'Confirmo que tenho autorização para aceder e utilizar os ficheiros indicados e que não estou a adicionar fontes de cópias não autorizadas de jogos comerciais.', saveSource:'Guardar fonte localmente', customSaved:'Fonte guardada neste navegador.', remove:'Remover', noCustom:'Ainda não guardaste fontes personalizadas.', invalidUrl:'Introduz um URL HTTPS válido.', githubOnly:'Para consultar automaticamente releases, introduz um URL de repositório GitHub (https://github.com/autor/repo). Outras páginas ficam guardadas como links externos.',
      sourceTypes:'Tipos de fonte', sourceVerified:'Hash publicado', sourceVerifiedText:'O download é comparado com o SHA-256 publicado antes de poder ser guardado.', sourceExternal:'Página externa', sourceExternalText:'Abre a página oficial do fornecedor. O Atlas não contorna CAPTCHA, autenticação nem links temporários.', sourceUnknown:'Não verificado', sourceUnknownText:'Sem hash/origem verificável, só é apresentada a página da fonte; não se afirma que o ficheiro é seguro.',
      privacyTitle:'Privacidade e limitações', privacyText:'A fila e as fontes personalizadas ficam neste navegador. O Atlas não aloja ficheiros nem envia relatórios. Downloads diretos exigem CORS e espaço de memória; o limite é 120 MB por ficheiro.',
      exportSettings:'Exportar fila e fontes', importSettings:'Importar fila/fontes', exportDone:'Exportação preparada.', importDone:'Dados importados.', importInvalid:'O ficheiro não tem formato compatível.', confirmClear:'Limpar a fila de downloads?',
      browserOnly:'A fila é local. Se fechares ou recarregares a página, partes de download não guardadas na memória são perdidas.', externalProvider:'Fornecedor externo', sourceName:'Fonte', retry:'Tentar novamente', noRepoRelease:'Não foi possível consultar releases. Abre a página oficial do repositório.',
      verifyBeforeUse:'Verifica sempre a licença, a origem e as permissões do ficheiro antes de o utilizar.'
    },
    en: {
      loading:'Verifying signature and fetching the homebrew.page catalogue…', loaded:'Catalogue signature and index hash verified', unavailable:'Could not fetch the live catalogue. Open the official source or try again.',
      catalogCount:n=>`${n} available apps in the catalogue`, noApps:'No apps match this search.', searchPlaceholder:'Search app, author or Title ID…',
      refresh:'Refresh catalogue ↻', catalog:'Community homebrew catalogue', detail:'Details', addQueue:'Add to queue', release:'Official release ↗', repo:'Source code ↗',
      titleId:'Title ID', author:'Author', version:'Version', license:'License', format:'Format', size:'Size', released:'Released', description:'Description', releaseNotes:'Release notes', detailsLoading:'Verifying and fetching details…', detailsUnavailable:'Could not retrieve signed details. Open the catalogue page or try again.', safety:'Informational scan',
      safetyStays:'Published scan found no sandbox escape', safetyLeaves:'Package is marked/detected as able to leave the sandbox', safetyUnclear:'Inconclusive safety scan', safetyUnknown:'No scan data',
      queueEmpty:'The queue is empty.', queueQueued:'Queued', queueDownloading:'Downloading', queuePaused:'Paused', queueVerified:'Hash verified — ready to save', queueSaved:'Downloaded and saved by the user', queueError:'Failed', queueCancelled:'Cancelled', queueExternal:'Direct transfer unavailable; open the official release.',
      startQueue:'Start queue', pause:'Pause', resume:'Resume', cancel:'Cancel', saveFile:'Save verified file', openRelease:'Open official release ↗', clearQueue:'Clear', added:'Added to queue.',
      checksumMissing:'No published SHA-256; only the official source page is available.', checksumInvalid:'The file URL is not on an approved release domain.', tooLarge:'File exceeds the 120 MB browser-transfer limit. Use the official release page.',
      checksumMismatch:'SHA-256 does not match the catalogue. The file was rejected.', checksumPassed:'SHA-256 verified.', browserNoCors:'The provider does not allow direct transfer from this site (CORS). Open the official release.',
      providersTitle:'Other official tools and stores', providersIntro:'Official project pages. The Atlas does not import the game catalogs from these applications.',
      sourceHomebrew:'Community catalogue', sourceTool:'Homebrew project', sourceProvider:'External provider (manual)', openProvider:'Open provider page ↗', checkRelease:'Check latest release',
      orbitDescription:'PS5 homebrew store; visit the project and its official releases.', spectrumDescription:'Community library/store application; visit the project and its official releases.',
      vikingDescription:'No automatic connector: open the provider page and follow its site flow. The Atlas does not bypass CAPTCHA, login or temporary links.',
      homebrewPageDescription:'Community catalog of native PS5 apps with project pages, releases and published hashes.', ps5LibraryDescription:'Self-hosted library platform for homebrew and content the operator is authorized to use; the catalog/server is managed by the user.',
      loadingRelease:'Checking release…', latestRelease:'Latest release', noAssets:'The release has no attached files.', assetHash:'Published SHA-256', assetNoHash:'No digest available through the API — open the release to verify.',
      customTitle:'Custom sources', customIntro:'Save project/release pages you are authorized to use. Sources remain in your browser and are not published.',
      customName:'Source name', customUrl:'Project/release page URL', customNamePlaceholder:'My authorized project', customUrlPlaceholder:'https://github.com/author/project',
      customConsent:'I confirm I am authorized to access and use the listed files, and I am not adding sources for unauthorized copies of commercial games.', saveSource:'Save source locally', customSaved:'Source saved in this browser.', remove:'Remove', noCustom:'No custom sources saved yet.', invalidUrl:'Enter a valid HTTPS URL.', githubOnly:'To query releases automatically, enter a GitHub repository URL (https://github.com/owner/repo). Other pages are saved as external links.',
      sourceTypes:'Source types', sourceVerified:'Published hash', sourceVerifiedText:'The download is compared with the published SHA-256 before it can be saved.', sourceExternal:'External page', sourceExternalText:'Opens the provider page. The Atlas does not bypass CAPTCHA, authentication or temporary links.', sourceUnknown:'Unverified', sourceUnknownText:'Without a verifiable hash/origin, only the source page is shown; the file is not claimed to be safe.',
      privacyTitle:'Privacy and limitations', privacyText:'The queue and custom sources stay in this browser. The Atlas does not host files or upload reports. Direct downloads require CORS and browser memory; the per-file limit is 120 MB.',
      exportSettings:'Export queue and sources', importSettings:'Import queue/sources', exportDone:'Export prepared.', importDone:'Data imported.', importInvalid:'The file format is not compatible.', confirmClear:'Clear the download queue?',
      browserOnly:'The queue is local. Reloading or closing the page discards partial data that has not been saved.', externalProvider:'External provider', sourceName:'Source', retry:'Try again', noRepoRelease:'Could not query releases. Open the repository’s official page.',
      verifyBeforeUse:'Always check the license, provenance and permissions before using a file.'
    }
  };
  const t = key => (T[language] && T[language][key]) || T.pt[key] || key;
  const memory = new Map();
  function getLocal(key, fallback) { try { const v = localStorage.getItem(key); return v == null ? fallback : v; } catch { return memory.has(key) ? memory.get(key) : fallback; } }
  function setLocal(key, value) { try { localStorage.setItem(key, value); } catch { memory.set(key, String(value)); } }
  function parseJson(raw, fallback) { try { return JSON.parse(raw); } catch { return fallback; } }
  const nowIso = () => new Date().toISOString();
  const providerDefinitions = [
    {id:'homebrew-page',name:'homebrew.page',kind:'catalogue',url:'https://homebrew.page',descriptionKey:'homebrewPageDescription',api:INDEX_URL},
    {id:'orbit-store',name:'Orbit Store',kind:'project',url:'https://github.com/saawant12/orbit-store-ps5',repo:'saawant12/orbit-store-ps5',descriptionKey:'orbitDescription'},
    {id:'spectrum-library',name:'Spectrum Library',kind:'project',url:'https://github.com/Phoenixx1202/Spectrum-Library',repo:'Phoenixx1202/Spectrum-Library',descriptionKey:'spectrumDescription'},
    {id:'ps5-library',name:'PS5Library',kind:'project',url:'https://github.com/rdiol12/PS5Library',repo:'rdiol12/PS5Library',descriptionKey:'ps5LibraryDescription'},
    {id:'vikingfile',name:'Vikingfile',kind:'external',url:'https://vikingfile.com/',descriptionKey:'vikingDescription'}
  ];
  let catalogApps = [];
  const catalogDetails = new Map();
  let catalogFetchedAt = '';
  let verifiedCatalogManifest = null;
  let activeRepoAssets = {};
  let isLoadingCatalog = false;
  let isProcessingQueue = false;
  const runtime = new Map();
  let queue = parseJson(getLocal(STORAGE_QUEUE, '[]'), []);
  let customSources = parseJson(getLocal(STORAGE_SOURCES, '[]'), []);
  if (!Array.isArray(queue)) queue = [];
  if (!Array.isArray(customSources)) customSources = [];
  // Only in-memory partial chunks survive pauses. Reloading cannot claim that bytes remain.
  queue = queue.map(item => {
    if (['downloading','paused','verified'].includes(item.status)) return {...item,status:'queued',progress:0,note: t('browserOnly')};
    return item;
  });
  saveQueue();

  function saveQueue() { setLocal(STORAGE_QUEUE, JSON.stringify(queue)); }
  function saveCustomSources() { setLocal(STORAGE_SOURCES, JSON.stringify(customSources)); }
  function setCatalogStatus(message, state='info') {
    const dot = $('#catalogStatusDot'); const text = $('#catalogStatusText');
    if (text) text.textContent = message;
    if (dot) { dot.className = `status-dot catalog-dot-${state}`; }
  }
  function safeUrl(value) {
    try { const url = new URL(value); if (url.protocol !== 'https:' || url.username || url.password) return null; return url; } catch { return null; }
  }
  function approvedDownloadUrl(value) {
    const url = safeUrl(value);
    return url && ACCEPTED_DOWNLOAD_HOSTS.has(url.hostname.toLowerCase()) ? url : null;
  }
  function parseRepoUrl(value) {
    const url = safeUrl(value);
    if (!url || url.hostname.toLowerCase() !== 'github.com') return null;
    const parts = url.pathname.split('/').filter(Boolean);
    if (parts.length !== 2 || ['features','topics','collections','marketplace','orgs','settings'].includes(parts[0].toLowerCase())) return null;
    const owner = parts[0], repo = parts[1].replace(/\.git$/i, '');
    if (!/^[A-Za-z0-9_.-]{1,100}$/.test(owner) || !/^[A-Za-z0-9_.-]{1,100}$/.test(repo)) return null;
    return {owner,repo,fullName:`${owner}/${repo}`,url:`https://github.com/${owner}/${repo}`,releaseUrl:`https://github.com/${owner}/${repo}/releases`};
  }
  function safeSourcePage(value) {
    const url = safeUrl(value || '');
    return url ? url.href : 'https://homebrew.page/';
  }
  function hexToBytes(hex) {
    if (!/^(?:[0-9a-f]{2})+$/i.test(String(hex || ''))) throw new Error('Invalid hexadecimal bytes');
    const out = new Uint8Array(hex.length / 2);
    for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
    return out;
  }
  async function sha256Hex(bytes) {
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, '0')).join('');
  }
  async function getVerifiedCatalogManifest(force = false) {
    if (!force && verifiedCatalogManifest && Date.now() - verifiedCatalogManifest.verifiedAt < 5 * 60 * 1000) {
      return verifiedCatalogManifest;
    }
    if (!crypto?.subtle?.importKey || !crypto?.subtle?.verify) {
      throw new Error(language === 'pt' ? 'Este navegador não suporta a verificação de assinatura Ed25519 exigida pelo catálogo.' : 'This browser cannot verify the Ed25519 signature required by the catalogue.');
    }
    const [manifestResponse, signatureResponse] = await Promise.all([
      fetch(`${API_ROOT}/manifest.json`, {headers:{'Accept':'application/json'},cache:'no-store'}),
      fetch(`${API_ROOT}/manifest.sig`, {cache:'no-store'})
    ]);
    if (!manifestResponse.ok || !signatureResponse.ok) throw new Error('Could not retrieve the signed homebrew catalogue manifest.');
    const manifestBytes = await manifestResponse.arrayBuffer();
    const signatureBytes = await signatureResponse.arrayBuffer();
    if (signatureBytes.byteLength !== 64) throw new Error('The catalogue signature has an unexpected length.');
    let signatureValid = false;
    for (const keyHex of CATALOG_PUBLIC_KEYS) {
      try {
        const key = await crypto.subtle.importKey('raw', hexToBytes(keyHex), {name:'Ed25519'}, false, ['verify']);
        if (await crypto.subtle.verify({name:'Ed25519'}, key, signatureBytes, manifestBytes)) { signatureValid = true; break; }
      } catch (error) {
        if (error?.name === 'NotSupportedError' || error?.name === 'SyntaxError') continue;
        // A single rejected key should not prevent trying the documented fallback key.
      }
    }
    if (!signatureValid) throw new Error('The homebrew catalogue signature could not be verified. No catalogue data was accepted.');
    let manifest;
    try { manifest = JSON.parse(new TextDecoder().decode(manifestBytes)); }
    catch { throw new Error('The signed catalogue manifest is not valid JSON.'); }
    if (!manifest || !manifest.files || !Number.isSafeInteger(Number(manifest.sequence))) throw new Error('The signed catalogue manifest has an invalid schema.');
    const sequence = Number(manifest.sequence);
    const highestSeen = Number(getLocal(STORAGE_CATALOG_SEQUENCE, '0')) || 0;
    if (sequence < highestSeen) throw new Error('The catalogue sequence is older than the last accepted version; refusing a rollback.');
    setLocal(STORAGE_CATALOG_SEQUENCE, String(Math.max(sequence, highestSeen)));
    verifiedCatalogManifest = {manifest, verifiedAt:Date.now()};
    return verifiedCatalogManifest;
  }
  async function fetchVerifiedCatalogJson(relativePath) {
    if (!/^(?:index\.json|apps\/[A-Za-z0-9_-]{1,40}\.json)$/.test(relativePath)) throw new Error('Unsupported catalogue JSON path.');
    for (let attempt = 0; attempt < 2; attempt++) {
      const state = await getVerifiedCatalogManifest(attempt > 0);
      const expected = String(state.manifest.files[relativePath] || '').toLowerCase();
      if (!/^[0-9a-f]{64}$/.test(expected)) throw new Error('The requested JSON file is not listed in the signed manifest.');
      const response = await fetch(`${API_ROOT}/${relativePath}`, {headers:{'Accept':'application/json'},cache:'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const raw = await response.arrayBuffer();
      if (await sha256Hex(raw) !== expected) {
        verifiedCatalogManifest = null;
        if (attempt === 0) continue;
        throw new Error('Catalogue file SHA-256 differs from its signed manifest. The file was rejected.');
      }
      try { return JSON.parse(new TextDecoder().decode(raw)); }
      catch { throw new Error('Verified catalogue file is not valid JSON.'); }
    }
    throw new Error('The catalogue changed during verification. Try again.');
  }
  function trustedMetaFromHomebrew(item, detail) {
    const url = approvedDownloadUrl(detail?.artifact_url || item.artifact_url || '');
    const hash = String(detail?.sha256 || item.sha256 || '').toLowerCase();
    if (!url || !/^[0-9a-f]{64}$/.test(hash)) return null;
    return {url:url.href,sha256:hash,size:Number(detail?.size ?? item.size) || null,sourcePage:safeSourcePage(detail?.release_url || detail?.page || item.page || item.source_repo || 'https://homebrew.page/'),sourceName:'homebrew.page',fileName:detail?.artifact_name || url.pathname.split('/').pop() || `${item.name}.zip`,license:detail?.license || item.license || ''};
  }
  function bytesFromHex(hex) { const out = new Uint8Array(hex.length/2); for (let i=0;i<out.length;i++) out[i]=parseInt(hex.slice(i*2,i*2+2),16); return out; }
  function renderProviderCards() {
    const root = $('#officialToolSources');
    if (!root) return;
    root.innerHTML = providerDefinitions.map(provider => {
      const label = provider.kind === 'catalogue' ? t('sourceHomebrew') : provider.kind === 'external' ? t('sourceProvider') : t('sourceTool');
      const pageAction = `<a class="control-button" href="${esc(provider.url)}" target="_blank" rel="noopener noreferrer">${t('openProvider')}</a>`;
      const releaseAction = provider.repo ? `<button class="control-button" type="button" data-load-release="${esc(provider.id)}">${t('checkRelease')}</button>` : '';
      const statusId = `provider-assets-${provider.id}`;
      return `<article class="provider-card"><div class="provider-card-top"><div><span class="source-type">${esc(label)}</span><h4>${esc(provider.name)}</h4></div><span class="provider-mark">↗</span></div><p>${esc(t(provider.descriptionKey))}</p><div class="provider-card-actions">${pageAction}${releaseAction}</div><div id="${statusId}" class="provider-assets"></div></article>`;
    }).join('');
    $$('[data-load-release]').forEach(button => button.addEventListener('click', () => loadProviderRelease(button.dataset.loadRelease)));
  }
  async function loadHomebrewCatalog() {
    if (isLoadingCatalog) return;
    isLoadingCatalog = true;
    const refreshButton = $('#refreshHomebrewCatalog');
    if (refreshButton) refreshButton.disabled = true;
    setCatalogStatus(t('loading'), 'loading');
    $('#homebrewCatalogGrid').innerHTML = `<div class="download-empty">${esc(t('loading'))}</div>`;
    try {
      const data = await fetchVerifiedCatalogJson('index.json');
      if (!data || !Array.isArray(data.apps)) throw new Error('Invalid signed catalogue schema');
      catalogApps = data.apps.filter(app => app && app.name && app.titleid && app.status !== 'coming_soon');
      catalogDetails.clear();
      catalogFetchedAt = data.generated || nowIso();
      setCatalogStatus(`${t('loaded')} · ${t('catalogCount')(catalogApps.length)}`, 'success');
      $('#catalogUpdatedAt').textContent = dateLabel(catalogFetchedAt);
      $('#downloadCatalogCount').textContent = catalogApps.length;
      renderHomebrewCatalog();
    } catch (error) {
      setCatalogStatus(`${t('unavailable')} (${String(error.message || error)})`, 'warning');
      $('#catalogUpdatedAt').textContent = '';
      $('#homebrewCatalogGrid').innerHTML = `<div class="download-empty"><p>${esc(t('unavailable'))}</p><a href="https://homebrew.page/" target="_blank" rel="noopener noreferrer">homebrew.page ↗</a></div>`;
    } finally {
      isLoadingCatalog = false;
      if (refreshButton) refreshButton.disabled = false;
    }
  }
  function renderHomebrewCatalog() {
    const root = $('#homebrewCatalogGrid');
    if (!root) return;
    const query = String($('#homebrewSearch')?.value || '').trim().toLowerCase();
    const filtered = catalogApps.filter(app => [app.name,app.author,app.titleid,app.description,app.version,app.license].join(' ').toLowerCase().includes(query));
    $('#downloadCatalogCount').textContent = catalogApps.length;
    if (!filtered.length) { root.innerHTML = `<div class="download-empty">${esc(t('noApps'))}</div>`; return; }
    root.innerHTML = filtered.map(app => {
      const iconRaw = app.icon_small || app.icon || '';
      const iconUrl = safeUrl(iconRaw);
      const icon = iconUrl ? iconUrl.href : '';
      const sandbox = app.safety?.sandbox || app.sandbox;
      const safety = sandbox === 'stays' ? t('safetyStays') : sandbox === 'leaves' ? t('safetyLeaves') : sandbox === 'unclear' ? t('safetyUnclear') : t('safetyUnknown');
      const downloadable = app.status === 'available' && /^[A-Za-z0-9_-]{1,40}$/.test(String(app.titleid || ''));
      const detailsId = `homebrew-details-${String(app.titleid || '').replace(/[^A-Za-z0-9_-]/g,'')}`;
      return `<article class="homebrew-card"><div class="homebrew-card-header">${icon ? `<img src="${esc(icon)}" alt="" loading="lazy" referrerpolicy="no-referrer">` : `<span class="homebrew-placeholder">⌘</span>`}<div class="homebrew-title"><h4>${esc(app.name)}</h4><p>${esc(app.author || '—')} · ${esc(app.titleid)}</p></div><span class="homebrew-version">${esc(app.version || '—')}</span></div><div class="homebrew-metadata"><span>${esc(t('format'))}: ${esc(app.format || '—')}</span><span>${esc(t('size'))}: ${esc(fmtSize(app.size))}</span><span>${esc(t('released'))}: ${esc(dateLabel(app.released))}</span></div><div class="homebrew-safety">${esc(safety)}</div><div class="homebrew-actions"><button class="control-button" type="button" data-detail-homebrew="${esc(app.titleid)}">${esc(t('detail'))}</button>${downloadable ? `<button class="primary-button" type="button" data-add-homebrew="${esc(app.titleid)}">${esc(t('addQueue'))}</button>` : ''}</div><div id="${esc(detailsId)}" class="homebrew-details"></div></article>`;
    }).join('');
    $$('[data-add-homebrew]').forEach(button => button.addEventListener('click', () => addHomebrewAppToQueue(button.dataset.addHomebrew)));
    $$('[data-detail-homebrew]').forEach(button => button.addEventListener('click', () => loadHomebrewAppDetails(button.dataset.detailHomebrew)));
  }
  async function getHomebrewAppDetails(titleId) {
    if (!/^[A-Za-z0-9_-]{1,40}$/.test(String(titleId || ''))) throw new Error('Invalid Title ID in catalogue.');
    if (catalogDetails.has(titleId)) return catalogDetails.get(titleId);
    const detail = await fetchVerifiedCatalogJson(`apps/${titleId}.json`);
    if (detail.titleid && String(detail.titleid) !== String(titleId)) throw new Error('The signed app record does not match the requested Title ID.');
    catalogDetails.set(titleId, detail);
    return detail;
  }
  async function loadHomebrewAppDetails(titleId) {
    const detailRoot = $(`#homebrew-details-${CSS.escape(titleId)}`);
    if (!detailRoot) return;
    detailRoot.innerHTML = `<p class="provider-loading">${esc(t('detailsLoading'))}</p>`;
    try {
      const detail = await getHomebrewAppDetails(titleId);
      const releaseUrl = safeSourcePage(detail.release_url || detail.page || 'https://homebrew.page/');
      const repoUrl = safeSourcePage(detail.source_repo || detail.release_url || 'https://homebrew.page/');
      const releaseNotes = String(detail.release_notes || '').trim();
      detailRoot.innerHTML = `<div class="homebrew-detail-body"><p>${esc(detail.description || '—')}</p><div class="homebrew-metadata"><span>${esc(t('license'))}: ${esc(detail.license || '—')}</span><span>${esc(t('format'))}: ${esc(detail.format || '—')}</span><span>${esc(t('size'))}: ${esc(fmtSize(detail.size))}</span></div>${releaseNotes ? `<div class="homebrew-release-notes"><strong>${esc(t('releaseNotes'))}</strong><p>${esc(releaseNotes.slice(0,3000))}</p></div>` : ''}<div class="provider-card-actions"><a class="control-button" href="${esc(releaseUrl)}" target="_blank" rel="noopener noreferrer">${esc(t('release'))}</a><a class="control-button" href="${esc(repoUrl)}" target="_blank" rel="noopener noreferrer">${esc(t('repo'))}</a></div></div>`;
    } catch (error) {
      detailRoot.innerHTML = `<div class="download-empty"><p>${esc(t('detailsUnavailable'))}</p><a href="https://homebrew.page/" target="_blank" rel="noopener noreferrer">homebrew.page ↗</a><small>${esc(String(error.message || error))}</small></div>`;
    }
  }
  async function addHomebrewAppToQueue(titleId) {
    const app = catalogApps.find(item => item.titleid === titleId);
    if (!app) return;
    const button = $(`[data-add-homebrew="${CSS.escape(titleId)}"]`);
    if (button) { button.disabled = true; button.textContent = t('loading'); }
    try {
      const detail = await getHomebrewAppDetails(titleId);
      const meta = trustedMetaFromHomebrew(app, detail);
      if (!meta) {
        if (button) { button.disabled = false; button.textContent = t('addQueue'); }
        alert(t('checksumMissing'));
        await loadHomebrewAppDetails(titleId);
        return;
      }
      enqueue({...meta,name:detail.name || app.name,titleId:detail.titleid || app.titleid,license:detail.license || app.license || '',version:detail.version || app.version || '',type:'homebrew-catalogue'});
      if (button) { button.disabled = false; button.textContent = t('added'); }
    } catch (error) {
      if (button) { button.disabled = false; button.textContent = t('addQueue'); }
      alert(`${t('checksumMissing')}\n${String(error.message || error)}`);
      await loadHomebrewAppDetails(titleId);
    }
  }
  function enqueue(meta) {
    const url = approvedDownloadUrl(meta.url);
    if (!url) { alert(t('checksumInvalid')); return; }
    if (!/^[0-9a-f]{64}$/i.test(String(meta.sha256 || ''))) { alert(t('checksumMissing')); return; }
    if (queue.some(item => item.url === url.href && item.sha256 === String(meta.sha256).toLowerCase() && !['saved','cancelled'].includes(item.status))) {
      renderQueue(); return;
    }
    queue.push({id:`DL-${Date.now()}-${Math.random().toString(16).slice(2,8)}`,name:String(meta.name || meta.fileName || 'homebrew-download').slice(0,180),fileName:String(meta.fileName || 'download.bin').replace(/[\\/\\:*?"<>|]/g,'_').slice(0,180),url:url.href,sha256:String(meta.sha256).toLowerCase(),size:Number(meta.size)||null,sourcePage:safeSourcePage(meta.sourcePage),sourceName:meta.sourceName||'Official release',license:meta.license||'',version:meta.version||'',titleId:meta.titleId||'',status:'queued',progress:0,note:'',created_at:nowIso(),type:meta.type||'github-release'});
    saveQueue(); renderQueue();
  }
  function queueStatusLabel(status) {
    return ({queued:t('queueQueued'),downloading:t('queueDownloading'),paused:t('queuePaused'),verified:t('queueVerified'),saved:t('queueSaved'),error:t('queueError'),cancelled:t('queueCancelled'),external:t('queueExternal')})[status] || t('queueQueued');
  }
  function renderQueue() {
    const root = $('#downloadQueueList'); if (!root) return;
    $('#queueCount').textContent = queue.filter(item=>!['saved','cancelled'].includes(item.status)).length;
    saveQueue();
    if (!queue.length) { root.innerHTML = `<p class="download-empty">${esc(t('queueEmpty'))}</p>`; return; }
    root.innerHTML = queue.slice().reverse().map(item => {
      const pct = Math.max(0,Math.min(100,Number(item.progress)||0));
      const active = item.status === 'downloading';
      const runtimeItem = runtime.get(item.id);
      const canSave = item.status === 'verified' && runtimeItem?.blob;
      const external = item.status === 'external' || item.status === 'error';
      const note = item.note ? `<p class="queue-note">${esc(item.note)}</p>` : '';
      const actions = `${active ? `<button class="queue-action" data-pause="${esc(item.id)}">${t('pause')}</button>` : ''}${item.status === 'paused' ? `<button class="queue-action" data-resume="${esc(item.id)}">${t('resume')}</button>` : ''}${item.status === 'queued' ? `<button class="queue-action" data-run-one="${esc(item.id)}">${t('resume')}</button>` : ''}${canSave ? `<button class="queue-action queue-action-save" data-save="${esc(item.id)}">${t('saveFile')}</button>` : ''}${external ? `<a class="queue-action" href="${esc(safeSourcePage(item.sourcePage))}" target="_blank" rel="noopener noreferrer">${t('openRelease')}</a>` : ''}${!['saved','cancelled'].includes(item.status) ? `<button class="queue-action queue-action-cancel" data-cancel="${esc(item.id)}">${t('cancel')}</button>` : ''}`;
      return `<article class="queue-item"><div class="queue-item-top"><div><strong>${esc(item.name)}</strong><small>${esc(item.sourceName)} · ${esc(fmtSize(item.size))}</small></div><span class="queue-state queue-state-${esc(item.status)}">${esc(queueStatusLabel(item.status))}</span></div>${active || item.status === 'paused' ? `<div class="queue-progress"><span style="width:${pct}%"></span></div><small class="queue-progress-label">${pct.toFixed(1)}%${item.size ? ` · ${fmtSize(runtimeItem?.loaded || item.size*pct/100)} / ${fmtSize(item.size)}` : ''}</small>` : ''}${note}<div class="queue-item-actions">${actions}</div></article>`;
    }).join('');
    $$('[data-pause]').forEach(btn=>btn.addEventListener('click',()=>pauseDownload(btn.dataset.pause)));
    $$('[data-resume],[data-run-one]').forEach(btn=>btn.addEventListener('click',()=>{ const id=btn.dataset.resume||btn.dataset.runOne; const item=queue.find(q=>q.id===id); if(item && ['paused','queued'].includes(item.status)){item.status='queued';item.note='';saveQueue();renderQueue();processQueue(id);} }));
    $$('[data-cancel]').forEach(btn=>btn.addEventListener('click',()=>cancelDownload(btn.dataset.cancel)));
    $$('[data-save]').forEach(btn=>btn.addEventListener('click',()=>saveVerifiedFile(btn.dataset.save)));
  }
  function pauseDownload(id) {
    const item = queue.find(q=>q.id===id); const rt=runtime.get(id);
    if (!item || !rt?.controller) return;
    rt.pauseRequested = true; item.status='paused'; item.note=t('browserOnly');
    rt.controller.abort(); saveQueue(); renderQueue();
  }
  function cancelDownload(id) {
    const item = queue.find(q=>q.id===id); const rt=runtime.get(id);
    if (rt?.controller) { rt.cancelRequested = true; rt.controller.abort(); }
    if (item) { item.status='cancelled'; item.progress=0; item.note=t('queueCancelled'); }
    runtime.delete(id); saveQueue(); renderQueue();
  }
  async function processQueue(preferredId=null) {
    if (isProcessingQueue) return;
    isProcessingQueue=true;
    try {
      while (true) {
        const item = preferredId ? queue.find(q=>q.id===preferredId && q.status==='queued') : queue.find(q=>q.status==='queued');
        preferredId=null;
        if (!item) break;
        const result = await processOne(item);
        if (result === 'paused') break;
      }
    } finally { isProcessingQueue=false; renderQueue(); }
  }
  async function processOne(item) {
    const url = approvedDownloadUrl(item.url);
    if (!url) { item.status='error';item.note=t('checksumInvalid');saveQueue();return 'error'; }
    if (!item.sha256 || !/^[0-9a-f]{64}$/i.test(item.sha256)) { item.status='external';item.note=t('checksumMissing');saveQueue();return 'external'; }
    if (item.size && item.size > MAX_BROWSER_DOWNLOAD) {
      const existing=runtime.get(item.id);if(existing){existing.chunks=[];existing.loaded=0;existing.blob=null;}
      item.status='external';item.note=t('tooLarge');saveQueue();return 'external';
    }
    let rt=runtime.get(item.id);
    if (!rt) { rt={chunks:[],loaded:0,controller:null,pauseRequested:false,cancelRequested:false,blob:null};runtime.set(item.id,rt); }
    item.status='downloading'; item.note=''; rt.pauseRequested=false; rt.cancelRequested=false;
    rt.controller=new AbortController();
    saveQueue();renderQueue();
    try {
      const headers = {};
      if (rt.loaded > 0) headers.Range = `bytes=${rt.loaded}-`;
      let response;
      try {
        response = await fetch(url.href,{headers,signal:rt.controller.signal,cache:'no-store'});
      } catch (error) {
        if (rt.loaded > 0 && error.name !== 'AbortError') {
          rt.chunks=[];rt.loaded=0;item.progress=0;item.note=language==='pt'?'O servidor não permitiu retomar; tenta novamente desde o início.':'The server did not allow resume; try again from the beginning.';
          item.status='queued';saveQueue();return 'retry';
        }
        throw error;
      }
      if (rt.loaded > 0 && response.status === 416) {
        rt.chunks=[];rt.loaded=0;item.progress=0;item.status='queued';
        item.note=language==='pt'?'O servidor recusou a retoma; a transferência vai recomeçar do início.':'The server rejected resume; the transfer will restart from the beginning.';
        saveQueue();return 'retry';
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      // If a server ignores Range and sends the whole file, discard partial chunks safely.
      if (rt.loaded > 0 && response.status !== 206) { rt.chunks=[];rt.loaded=0;item.progress=0; }
      const headerLength=Number(response.headers.get('content-length'))||0;
      let total=item.size || (response.status===206 ? Number((response.headers.get('content-range')||'').split('/').pop())||0 : headerLength);
      if (total > MAX_BROWSER_DOWNLOAD) { rt.chunks=[];rt.loaded=0;rt.blob=null;item.progress=0;item.status='external';item.note=t('tooLarge');saveQueue();return 'external'; }
      if (!response.body || !response.body.getReader) throw new Error('ReadableStream is unavailable in this browser');
      const reader=response.body.getReader(); let lastPaint=0;
      while (true) {
        const {done,value}=await reader.read(); if(done)break;
        const chunk = value instanceof Uint8Array ? value : new Uint8Array(value);
        // Enforce the limit from the streamed byte count, even if a server omits Content-Length.
        if (rt.loaded + chunk.byteLength > MAX_BROWSER_DOWNLOAD) {
          try { await reader.cancel(); } catch { /* best-effort stream cancellation */ }
          try { rt.controller.abort(); } catch { /* request may already have completed */ }
          rt.chunks=[];rt.loaded=0;item.progress=0;item.status='external';item.note=t('tooLarge');saveQueue();return 'external';
        }
        rt.chunks.push(chunk);rt.loaded+=chunk.byteLength;
        if (total) item.progress=Math.min(99.9,rt.loaded/total*100);
        const now=performance.now();
        if(now-lastPaint>250){saveQueue();renderQueue();lastPaint=now;}
      }
      const bytes = new Uint8Array(rt.loaded); let offset=0;
      for (const chunk of rt.chunks) { bytes.set(chunk,offset);offset+=chunk.byteLength; }
      const digestBytes = await crypto.subtle.digest('SHA-256',bytes.buffer);
      const digest=[...new Uint8Array(digestBytes)].map(n=>n.toString(16).padStart(2,'0')).join('');
      if(digest.toLowerCase()!==item.sha256.toLowerCase()) { item.status='error';item.progress=0;item.note=t('checksumMismatch');runtime.delete(item.id);saveQueue();return 'error'; }
      if(item.size && rt.loaded !== item.size) { item.status='error';item.progress=0;item.note=language==='pt'?'O tamanho transferido difere do tamanho publicado; o ficheiro foi rejeitado.':'Downloaded size differs from the published size; the file was rejected.';runtime.delete(item.id);saveQueue();return 'error'; }
      rt.blob=new Blob([bytes],{type:'application/octet-stream'});rt.chunks=[];rt.loaded=bytes.byteLength;
      item.status='verified';item.progress=100;item.note=t('checksumPassed');saveQueue();renderQueue();return 'verified';
    } catch(error) {
      if(rt.pauseRequested){item.status='paused';item.note=t('browserOnly');saveQueue();return 'paused';}
      if(rt.cancelRequested){item.status='cancelled';item.note=t('queueCancelled');saveQueue();return 'cancelled';}
      // A CORS/fetch TypeError means the browser cannot read the bytes. Do not proxy or bypass the host.
      if(error instanceof TypeError || /CORS|Failed to fetch|NetworkError/i.test(String(error.message||error))){item.status='external';item.note=t('browserNoCors');}
      else {item.status='error';item.note=`${String(error.message||error)}. ${t('queueExternal')}`;}
      saveQueue();return item.status;
    } finally { rt.controller=null;renderQueue(); }
  }
  function saveVerifiedFile(id) {
    const item=queue.find(q=>q.id===id), rt=runtime.get(id);
    if(!item||!rt?.blob){alert(t('browserOnly'));return;}
    const url=URL.createObjectURL(rt.blob);const anchor=document.createElement('a');anchor.href=url;anchor.download=item.fileName||'homebrew-download.bin';document.body.appendChild(anchor);anchor.click();anchor.remove();
    setTimeout(()=>URL.revokeObjectURL(url),30000);
    item.status='saved';item.note=t('checksumPassed');saveQueue();renderQueue();
  }
  async function loadProviderRelease(providerId) {
    const provider=providerDefinitions.find(p=>p.id===providerId);
    if(!provider?.repo)return;
    const root=$(`#provider-assets-${CSS.escape(providerId)}`);if(!root)return;
    root.innerHTML=`<p class="provider-loading">${esc(t('loadingRelease'))}</p>`;
    try {
      const response=await fetch(`https://api.github.com/repos/${provider.repo}/releases/latest`,{headers:{'Accept':'application/vnd.github+json'}});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const release=await response.json();
      root.innerHTML=`<div class="provider-release-heading"><strong>${esc(t('latestRelease'))}: ${esc(release.tag_name||release.name||'—')}</strong><small>${esc(dateLabel(release.published_at))}</small></div>${(release.assets||[]).map(asset=>{
        const digest=String(asset.digest||'').replace(/^sha256:/i,'').toLowerCase();
        const isSafe=/^[0-9a-f]{64}$/.test(digest)&&approvedDownloadUrl(asset.browser_download_url);
        const meta={name:asset.name,fileName:asset.name,url:asset.browser_download_url,sha256:digest,size:asset.size,sourcePage:safeSourcePage(release.html_url||provider.url),sourceName:provider.name,type:'github-release'};
        return `<div class="provider-asset"><div><strong>${esc(asset.name)}</strong><small>${esc(fmtSize(asset.size))} · ${isSafe?t('assetHash'):t('assetNoHash')}</small></div><div class="provider-asset-actions"><a class="queue-action" href="${esc(release.html_url||provider.url)}" target="_blank" rel="noopener noreferrer">${t('openRelease')}</a>${isSafe?`<button type="button" class="queue-action" data-queue-release="${esc(providerId)}:${esc(asset.id)}">${t('addQueue')}</button>`:''}</div></div>`;
      }).join('')||`<p class="provider-loading">${esc(t('noAssets'))}</p>`}`;
      activeRepoAssets[providerId]={release,assets:release.assets||[],provider};
      $$('[data-queue-release]',root).forEach(button=>button.addEventListener('click',()=>{
        const [pid,assetId]=button.dataset.queueRelease.split(':');const state=activeRepoAssets[pid];const asset=state?.assets.find(a=>String(a.id)===assetId);if(!asset)return;
        const digest=String(asset.digest||'').replace(/^sha256:/i,'').toLowerCase();
        if(!/^[0-9a-f]{64}$/.test(digest)){alert(t('checksumMissing'));return;}
        enqueue({name:asset.name,fileName:asset.name,url:asset.browser_download_url,sha256:digest,size:asset.size,sourcePage:safeSourcePage(state.release.html_url||state.provider.url),sourceName:state.provider.name,type:'github-release'});
        button.textContent=t('added');
      }));
    } catch(error) {root.innerHTML=`<p class="provider-loading">${esc(t('noRepoRelease'))} (${esc(String(error.message||error))}) <a href="${esc(provider.url+'/releases')}" target="_blank" rel="noopener noreferrer">${t('openRelease')}</a></p>`;}
  }
  function renderCustomSources() {
    const root=$('#customSourcesList');if(!root)return;
    if(!customSources.length){root.innerHTML=`<p class="download-empty">${esc(t('noCustom'))}</p>`;return;}
    root.innerHTML=customSources.map(source=>{
      const repo=source.repo;
      return `<article class="custom-source-item"><div><strong>${esc(source.name)}</strong><small>${esc(source.url)}</small>${repo?`<small>${esc(repo.fullName)} · ${esc(t('sourceName'))}</small>`:''}</div><div class="custom-source-actions">${repo?`<button type="button" class="queue-action" data-custom-release="${esc(source.id)}">${t('checkRelease')}</button>`:''}<a class="queue-action" href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${t('openProvider')}</a><button type="button" class="queue-action queue-action-cancel" data-remove-source="${esc(source.id)}">${t('remove')}</button></div><div class="provider-assets" id="custom-assets-${esc(source.id)}"></div></article>`;
    }).join('');
    $$('[data-remove-source]').forEach(button=>button.addEventListener('click',()=>{customSources=customSources.filter(s=>s.id!==button.dataset.removeSource);saveCustomSources();renderCustomSources();}));
    $$('[data-custom-release]').forEach(button=>button.addEventListener('click',()=>loadCustomRelease(button.dataset.customRelease)));
  }
  async function loadCustomRelease(id) {
    const source=customSources.find(s=>s.id===id && s.repo);if(!source)return;
    const root=$(`#custom-assets-${CSS.escape(id)}`);if(!root)return;
    root.innerHTML=`<p class="provider-loading">${esc(t('loadingRelease'))}</p>`;
    try {
      const response=await fetch(`https://api.github.com/repos/${source.repo.fullName}/releases/latest`,{headers:{'Accept':'application/vnd.github+json'}});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const release=await response.json();
      const assets=release.assets||[];activeRepoAssets[id]={release,assets,provider:{name:source.name,url:source.url}};
      root.innerHTML=`<div class="provider-release-heading"><strong>${esc(t('latestRelease'))}: ${esc(release.tag_name||release.name||'—')}</strong><small>${esc(dateLabel(release.published_at))}</small></div>${assets.map(asset=>{
        const digest=String(asset.digest||'').replace(/^sha256:/i,'').toLowerCase();
        const canQueue=/^[0-9a-f]{64}$/.test(digest)&&approvedDownloadUrl(asset.browser_download_url);
        return `<div class="provider-asset"><div><strong>${esc(asset.name)}</strong><small>${esc(fmtSize(asset.size))} · ${canQueue?t('assetHash'):t('assetNoHash')}</small></div><div class="provider-asset-actions"><a class="queue-action" href="${esc(release.html_url||source.url)}" target="_blank" rel="noopener noreferrer">${t('openRelease')}</a>${canQueue?`<button type="button" class="queue-action" data-custom-queue="${esc(id)}:${esc(asset.id)}">${t('addQueue')}</button>`:''}</div></div>`;
      }).join('')||`<p class="provider-loading">${esc(t('noAssets'))}</p>`}`;
      $$('[data-custom-queue]',root).forEach(button=>button.addEventListener('click',()=>{const [sid,aid]=button.dataset.customQueue.split(':');const state=activeRepoAssets[sid];const asset=state?.assets.find(a=>String(a.id)===aid);if(!asset)return;const digest=String(asset.digest||'').replace(/^sha256:/i,'').toLowerCase();enqueue({name:asset.name,fileName:asset.name,url:asset.browser_download_url,sha256:digest,size:asset.size,sourcePage:state.release.html_url||source.url,sourceName:source.name,type:'github-release'});button.textContent=t('added');}));
    }catch(error){root.innerHTML=`<p class="provider-loading">${esc(t('noRepoRelease'))} (${esc(String(error.message||error))})</p>`;}
  }
  function submitCustomSource(event) {
    event.preventDefault();
    const name=$('#customSourceNameInput').value.trim();const rawUrl=$('#customSourceUrlInput').value.trim();const consent=$('#customSourceConsent').checked;const feedback=$('#customSourceFeedback');
    if(!consent){feedback.textContent=t('customConsent');feedback.classList.remove('hidden');return;}
    const parsed=safeUrl(rawUrl);if(!parsed){feedback.textContent=t('invalidUrl');feedback.classList.remove('hidden');return;}
    const repo=parseRepoUrl(rawUrl);
    const record={id:`SRC-${Date.now()}-${Math.random().toString(16).slice(2,7)}`,name:name.slice(0,100),url:parsed.href,repo:repo||null,created_at:nowIso(),authorized:true};
    customSources.push(record);saveCustomSources();$('#customSourceForm').reset();feedback.textContent=repo?t('customSaved'):t('githubOnly');feedback.classList.remove('hidden');renderCustomSources();
  }
  function exportSettings() {
    const payload={schema_version:1,project:'PS5 Game Compatibility Atlas',exported_at:nowIso(),custom_sources:customSources,queue:queue.map(item=>({...item,status:['downloading','paused','verified'].includes(item.status)?'queued':item.status,progress:0}))};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='ps5-atlas-sources-and-download-queue.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
  }
  function importSettings(event) {
    const file=event.target.files?.[0];if(!file)return;
    const reader=new FileReader();reader.onload=()=>{
      const data=parseJson(String(reader.result||''),null);
      if(!data||data.schema_version!==1||!Array.isArray(data.custom_sources)||!Array.isArray(data.queue)){alert(t('importInvalid'));return;}
      customSources=data.custom_sources.filter(item=>item && typeof item.name==='string' && item.name.trim() && safeUrl(item.url)).slice(0,100).map(item=>({id:`SRC-${Date.now()}-${Math.random().toString(16).slice(2,7)}`,name:String(item.name).trim().slice(0,100),url:safeUrl(item.url).href,repo:parseRepoUrl(item.url),created_at:nowIso(),authorized:true}));
      queue=data.queue.filter(item=>item&&typeof item.name==='string'&&approvedDownloadUrl(item.url)&&/^[0-9a-f]{64}$/i.test(item.sha256||'')&&(!Number.isFinite(Number(item.size))||Number(item.size)>=0)).slice(-50).map(item=>({...item,name:String(item.name).slice(0,180),fileName:String(item.fileName||'download.bin').replace(/[\\/:*?"<>|]/g,'_').slice(0,180),size:Number(item.size)>0?Number(item.size):null,sha256:String(item.sha256).toLowerCase(),sourcePage:safeSourcePage(item.sourcePage),sourceName:String(item.sourceName||'Imported source').slice(0,100),status:'queued',progress:0,note:'',id:`DL-${Date.now()}-${Math.random().toString(16).slice(2,7)}`}));
      saveCustomSources();saveQueue();renderCustomSources();renderQueue();alert(t('importDone'));
    };reader.readAsText(file);event.target.value='';
  }
  function clearQueue() {
    if(!queue.length)return;
    if(!confirm(t('confirmClear')))return;
    for(const item of queue){const rt=runtime.get(item.id);if(rt?.controller){rt.cancelRequested=true;rt.controller.abort();}}
    queue=[];runtime.clear();saveQueue();renderQueue();
  }
  function applyDownloadLanguage(newLanguage) {
    language=newLanguage==='en'?'en':'pt';
    renderProviderCards();renderCustomSources();renderQueue();
    if(catalogApps.length)renderHomebrewCatalog();
    for(const [id,state] of Object.entries(activeRepoAssets)){
      const provider=state.provider;if(provider?.id)loadProviderRelease(provider.id);
      else if(id && customSources.some(s=>s.id===id))loadCustomRelease(id);
    }
  }

  $('#refreshHomebrewCatalog')?.addEventListener('click', loadHomebrewCatalog);
  $('#homebrewSearch')?.addEventListener('input', renderHomebrewCatalog);
  $('#customSourceForm')?.addEventListener('submit', submitCustomSource);
  $('#startDownloadQueue')?.addEventListener('click',()=>processQueue());
  $('#clearDownloadQueue')?.addEventListener('click',clearQueue);
  $('#exportDownloadSettings')?.addEventListener('click',exportSettings);
  $('#importDownloadSettings')?.addEventListener('change',importSettings);
  window.addEventListener('atlas-language-change',event=>applyDownloadLanguage(event.detail?.language||'pt'));

  renderProviderCards();renderQueue();renderCustomSources();
  // Load the community catalog only when the user opens the tab, avoiding unnecessary network calls.
  document.querySelector('[data-tab="downloads"]')?.addEventListener('click',()=>{if(!catalogApps.length&&!isLoadingCatalog)loadHomebrewCatalog();});
  // Keep status labels synchronized after a language toggle.
  if(catalogApps.length)renderHomebrewCatalog();
})();
