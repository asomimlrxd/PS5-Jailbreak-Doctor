(() => {
  'use strict';
  const DATA = window.ATLAS_DATA;
  if (!DATA || !Array.isArray(DATA.reports)) {
    document.body.innerHTML = '<main style="padding:32px;color:#fff;font-family:system-ui"><h1>Atlas data could not be loaded</h1><p>Check that data/atlas-data.js exists next to index.html.</p></main>';
    return;
  }

  const I18N = {
    pt: {
      brandTag:'Resultados da comunidade, com fontes', researchCutoff:'Pesquisa até 13 out. 2026', atlasCommunity:'Atlas comunitário', eyebrow:'PROJETO DE INVESTIGAÇÃO COMUNITÁRIO · PRÉ-VISUALIZAÇÃO 0.2.0',
      heroTitle:'Descobre o que funciona.<br><span>Vê primeiro a evidência.</span>', heroText:'Pesquisa relatos de jogos PS5 por firmware, formato e armazenamento. Cada resultado mantém a fonte original e distingue testes curtos, problemas por resolver e sessões concluídas.',
      pillSearch:'Pesquisa cruzada', pillSources:'Fontes originais', pillCommunity:'Relatos comunitários', gamesTracked:'jogos indexados', sourceLed:'Fontes públicas · Homebrew e downloads verificados',
      cautionBanner:'<strong>Importante:</strong> estes são resultados reportados, não garantias. Um jogo pode ter resultados diferentes consoante firmware, formato, versão, armazenamento ou integridade da origem.',
      metricGames:'JOGOS', metricGamesNote:'Títulos distintos nos relatos', metricReports:'RELATOS', metricReportsNote:'Observações com fonte', metricPlayable:'RELATOS SEM FALHA CRÍTICA', metricPlayableNote:'Inclui testes curtos e problemas menores', metricFormats:'FORMATOS', metricFormatsNote:'Guias separados da compatibilidade por jogo',
      tabGames:'Jogos e relatos', tabFormats:'Guia de formatos', tabDownloads:'Downloads & fontes', tabSources:'Fontes e metodologia', tabContribute:'Adicionar um teste',
      indexLabel:'ÍNDICE COMUNITÁRIO', catalogTitle:'Resultados de compatibilidade', catalogIntro:'Os resultados estão agrupados por jogo, mas cada configuração continua separada para não ocultar contradições.', resetFilters:'Limpar filtros ↺',
      searchPlaceholder:'Pesquisar jogo, Title ID, firmware, sintoma…', filterFirmware:'Firmware', allFirmwares:'Todos', filterFormat:'Formato', allFormats:'Todos', filterStorage:'Armazenamento', allStorage:'Todos', filterStatus:'Estado reportado', allStatuses:'Todos', sortBy:'Ordenar', sortRelevant:'Mais relatos primeiro', sortAlpha:'Nome do jogo A–Z', sortProblems:'Problemas primeiro',
      storageInternal:'SSD interno', storageExternalSsd:'SSD externo', storageUsb:'USB / HDD externo', reportNote:'Cada cartão mantém os testes separados por configuração', games:'jogos', reports:'relatos', matchedConfigurations:'configurações a corresponder aos filtros', emptyTitle:'Não foram encontrados resultados', emptyText:'Altera os filtros ou tenta outra pesquisa.', shownFrom:'A mostrar registos selecionados da base inicial.',
      statusCompleted:'Concluído sem problemas reportados', statusPlayableIssues:'Jogável com problemas', statusPlayableShort:'Teste curto / preliminar', statusResolved:'Problema resolvido no relato', statusLaunchFailed:'Não inicia / ecrã preto', statusCrashes:'Crash / freeze', statusMixed:'Relatos mistos', statusUnknown:'Estado não confirmado',
      noTitleId:'Title ID não indicado', reportCountOne:'relato', reportCountMany:'relatos', qualityHigh:'Evidência detalhada', qualityMedium:'Evidência média', qualityLow:'Evidência limitada', firmwareLabelShort:'FIRMWARE', formatLabelShort:'FORMATO', storageLabelShort:'ARMAZENAMENTO', testScope:'Âmbito do teste', reportedResolution:'RESOLUÇÃO REPORTADA', resolutionUnknown:'Não foi indicada solução.', openSource:'Abrir fonte original ↗', sourceLabel:'Fonte:',
      formatLabel:'FORMATO NÃO É GARANTIA', formatTitle:'Guia rápido de formatos', formatIntro:'As recomendações do mantenedor e os resultados de utilizadores são apresentados separadamente.', formatCalloutTitle:'Compatibilidade depende da configuração', formatCalloutText:'O mesmo jogo pode funcionar num formato e falhar noutro. Não existe, nestes dados, um formato universalmente melhor para todos os jogos, firmwares e unidades.',
      formatMethodTitle:'Como interpretar esta página', formatMethodText:'O estado de um formato vem da documentação do ShadowMountPlus. Os relatos individuais ficam no separador Jogos e relatos. Não somamos resultados diferentes como se fossem testes controlados.',
      recommended:'Recomendado', experimental:'Experimental', compatibilitySpecific:'Compatibilidade / títulos específicos', communityReports:'Relatos comunitários', documented:'Documentado', sourceOnDocs:'Fonte: documentação do ShadowMountPlus',
      researchLabel:'TRANSPARÊNCIA', sourcesTitle:'Fontes e metodologia', sourcesIntro:'A base inicial cruza documentação técnica, issues do GitHub e relatos públicos do Reddit. Cada cartão de jogo aponta para a origem que sustenta o resumo.', sourcesCountLabel:'fontes registadas', lowConfidenceLabel:'relatos com evidência limitada', never:'Downloads', noDownloadsLabel:'não alojamos jogos; ligamos apenas a ficheiros autorizados',
      methodEvidenceTitle:'O que significa a qualidade da evidência?', methodEvidenceText:'<strong>Alta</strong>: issue detalhada/reprodutível ou documentação do mantenedor. <strong>Média</strong>: configuração e resultado descritos com algum detalhe. <strong>Baixa</strong>: comentário curto, campos em falta ou resultado preliminar. Estes níveis descrevem a documentação do relato, não uma probabilidade estatística de sucesso.',
      rulesTitle:'Regras editoriais', rule1:'Um relato não equivale a compatibilidade universal. Os relatos contraditórios ficam separados.', rule2:'«Sem problemas até agora» é um teste preliminar; «jogo terminado» é evidência de maior alcance.', rule3:'Quando firmware, formato ou armazenamento não são indicados, o Atlas assinala o campo como desconhecido em vez de o adivinhar.', rule4:'Folhas históricas que listam o firmware mínimo/requisito do jogo não são misturadas com resultados de execução em homebrew.', rule5:'Os resumos são paráfrases. Consulta sempre a publicação original para o contexto completo e atualizações posteriores.',
      communityInput:'PARTICIPAÇÃO COMUNITÁRIA', contributeTitle:'Adicionar um resultado de teste', contributeIntro:'Regista uma observação com contexto suficiente para ser útil a outra pessoa.', formGameHeading:'Jogo e configuração', formGameHint:'Indica só aquilo que testaste.', gameNameLabel:'Nome do jogo *', firmwareLabel:'Firmware *', consoleLabel:'Consola', unknown:'Não indicado', gameVersionLabel:'Versão do jogo', formatLabel2:'Formato *', notSure:'Não sei / não indicado', storageLabel:'Armazenamento *', toolVersionsLabel:'Versões das ferramentas',
      formResultHeading:'Resultado observado', formResultHint:'Seleciona o resultado mais próximo.', symptomsLabel:'Sintomas / observações *', symptomsPlaceholder:'O que aconteceu? Durante quanto tempo testaste? Algum erro?', resolutionLabel:'Resolução (se aplicável)', resolutionPlaceholder:'O que mudou e se foi confirmado…', sourceUrlLabel:'Link para o post/issue público *', consentText:'Confirmo que é um resultado que observei ou uma fonte pública que estou a citar; não incluí dados pessoais.', saveReport:'Guardar resultado localmente', localOnly:'Os resultados submetidos ficam apenas neste navegador. Não são enviados para um servidor.', formSaved:'Resultado guardado apenas neste navegador.',
      localPanelTitle:'Contribuições locais', localPanelText:'Este protótipo não tem backend central. Exporta os teus resultados em JSON para os reveres ou preparares uma contribuição ao repositório.', localSaved:'resultados guardados neste navegador', exportJson:'Exportar JSON', clearLocal:'Apagar contribuições locais', noLocalReports:'Ainda não guardaste resultados locais.', confirmClear:'Queres apagar todas as contribuições guardadas neste navegador?', localReport:'Resultado local', footerPreview:'Pré-visualização local · v0.2.0', footerNoAffiliation:'Projeto comunitário independente. Não afiliado à Sony.', footerDocumentation:'Documentação técnica ↗',
      sourceReports:'relatos associados', publicCommunity:'Comunidade pública', maintainerDocs:'Documentação do mantenedor', openSourceList:'Abrir fonte ↗', exportDatabase:'Exportar base de dados JSON', exportCsv:'Exportar registos CSV', copiedNoBackend:'O JSON foi descarregado. Para integrar relatos na base pública, revê a fonte e valida os campos antes de editar o dataset.',
      status_playable_short:'Teste curto / preliminar', status_playable_issues:'Jogável com problemas', status_completed:'Concluído sem problemas reportados', status_resolved:'Problema resolvido no relato', status_launch_failed:'Falha de arranque / ecrã preto', status_crashes:'Crash / freeze', status_unknown:'Estado não confirmado', status_mixed:'Relatos mistos',
      downloadsEyebrow:'FONTES OFICIAIS · FICHEIROS VERIFICÁVEIS', downloadsTitle:'Downloads & fontes', downloadsIntro:'Explora homebrew publicado pelos respetivos autores, consulta a origem, compara o SHA-256 e gere uma fila local de downloads.', refreshCatalog:'Atualizar catálogo ↻', downloadPolicyTitle:'Downloads de homebrew com origem identificada', downloadPolicyText:'O Atlas liga a releases oficiais e a catálogos de homebrew revistos. Verifica o hash quando existe um valor publicado. Não agrega nem distribui cópias não autorizadas de jogos comerciais. Os downloads externos podem exigir que abras a página do fornecedor.', catalogNotLoaded:'Catálogo ainda não carregado. Clica em «Atualizar catálogo».', officialHomebrewCatalog:'Catálogo comunitário de homebrew', catalogExplanation:'Dados do catálogo comunitário homebrew.page. Os ficheiros são alojados pelos respetivos projetos, não pelo Atlas.', homebrewSearchPlaceholder:'Pesquisar aplicação, autor ou Title ID…', catalogPrompt:'Carrega no botão para consultar o catálogo em direto.', otherOfficialTools:'Outros projetos homebrew', officialToolNote:'Páginas oficiais dos próprios projetos. O Atlas não importa os catálogos de jogos dessas aplicações.', customSourcesTitle:'Fontes personalizadas', customSourcesIntro:'Guarda páginas de projetos ou releases que tens autorização para usar. As fontes ficam no teu navegador e não são publicadas.', customSourceName:'Nome da fonte', customSourceUrl:'URL da página do projeto/release', customSourceNamePlaceholder:'O meu projeto autorizado', customSourceUrlPlaceholder:'https://github.com/autor/projeto', customSourceConsentText:'Confirmo que tenho autorização para aceder e utilizar os ficheiros indicados e que não estou a adicionar fontes de cópias não autorizadas de jogos comerciais.', saveCustomSource:'Guardar fonte localmente', downloadQueueTitle:'Fila de downloads', queueExplanation:'Os downloads compatíveis são transferidos no navegador e verificados contra o SHA-256 publicado. Se CORS ou o tamanho impedirem a transferência direta, abre a release oficial.', startQueue:'Iniciar fila', clearQueue:'Limpar', queueEmpty:'A fila está vazia.', sourceTypesTitle:'Tipos de fonte', sourceVerified:'Hash publicado', sourceVerifiedText:'O ficheiro é comparado com o SHA-256 indicado pelo catálogo antes de poder ser guardado.', sourceExternal:'Página externa', sourceExternalText:'Abre-se a página oficial do fornecedor; o Atlas não ultrapassa CAPTCHAs, autenticação nem ligações temporárias.', sourceUnknown:'Não verificado', sourceUnknownText:'Sem hash ou origem verificável, só se mostra a página da fonte; não se afirma que o ficheiro é seguro.', privacyDownloadTitle:'Privacidade e limites', privacyDownloadText:'A fila e as fontes guardadas ficam neste navegador. O Atlas não aloja ficheiros nem recebe logs. Downloads diretos requerem CORS e espaço de memória; existe um limite de tamanho.', exportDownloadSettings:'Exportar fontes e fila', importDownloadSettings:'Importar fontes guardadas',
    },
    en: {
      brandTag:'Sourced community reports', researchCutoff:'Research snapshot · 13 Oct 2026', atlasCommunity:'Community Atlas', eyebrow:'COMMUNITY RESEARCH PROJECT · PREVIEW 0.2.0',
      heroTitle:'Find what works.<br><span>Read the evidence first.</span>', heroText:'Search PS5 game reports by firmware, format and storage. Every result links to its original source and distinguishes short tests, unresolved problems and completed playthroughs.',
      pillSearch:'Cross-filtered search', pillSources:'Original sources', pillCommunity:'Community reports', gamesTracked:'games indexed', sourceLed:'Public sources · Homebrew and verified downloads',
      cautionBanner:'<strong>Important:</strong> these are reported results, not guarantees. A game may behave differently depending on firmware, format, version, storage or source integrity.',
      metricGames:'GAMES', metricGamesNote:'Distinct titles in reports', metricReports:'REPORTS', metricReportsNote:'Observations with sources', metricPlayable:'REPORTS WITHOUT CRITICAL FAILURE', metricPlayableNote:'Includes short tests and minor issues', metricFormats:'FORMATS', metricFormatsNote:'Format guidance is separate from title reports',
      tabGames:'Games & reports', tabFormats:'Format guide', tabDownloads:'Downloads & sources', tabSources:'Sources & methodology', tabContribute:'Add a test',
      indexLabel:'COMMUNITY INDEX', catalogTitle:'Compatibility reports', catalogIntro:'Records are grouped by game, but every configuration stays separate so conflicting results remain visible.', resetFilters:'Reset filters ↺',
      searchPlaceholder:'Search game, Title ID, firmware, symptom…', filterFirmware:'Firmware', allFirmwares:'All', filterFormat:'Format', allFormats:'All', filterStorage:'Storage', allStorage:'All', filterStatus:'Reported status', allStatuses:'All', sortBy:'Sort by', sortRelevant:'Most reports first', sortAlpha:'Game name A–Z', sortProblems:'Problems first',
      storageInternal:'Internal SSD', storageExternalSsd:'External SSD', storageUsb:'USB / external HDD', reportNote:'Each card keeps tests separate by configuration', games:'games', reports:'reports', matchedConfigurations:'configurations match the filters', emptyTitle:'No results found', emptyText:'Change the filters or try another search.', shownFrom:'Showing selected records from the starter dataset.',
      statusCompleted:'Completed with no issues reported', statusPlayableIssues:'Playable with issues', statusPlayableShort:'Short / preliminary test', statusResolved:'Issue resolved in report', statusLaunchFailed:'Launch failure / black screen', statusCrashes:'Crash / freeze', statusMixed:'Mixed reports', statusUnknown:'Status unconfirmed',
      noTitleId:'Title ID not stated', reportCountOne:'report', reportCountMany:'reports', qualityHigh:'Detailed evidence', qualityMedium:'Medium evidence', qualityLow:'Limited evidence', firmwareLabelShort:'FIRMWARE', formatLabelShort:'FORMAT', storageLabelShort:'STORAGE', testScope:'Test scope', reportedResolution:'REPORTED RESOLUTION', resolutionUnknown:'No resolution was reported.', openSource:'Open original source ↗', sourceLabel:'Source:',
      formatLabel:'FORMAT IS NOT A GUARANTEE', formatTitle:'Format quick guide', formatIntro:'Maintainer guidance and user observations are shown separately.', formatCalloutTitle:'Compatibility depends on the setup', formatCalloutText:'The same game may work in one format and fail in another. These records do not establish one universally best format across games, firmware and drives.',
      formatMethodTitle:'How to read this section', formatMethodText:'Format status comes from ShadowMountPlus documentation. Individual reports are in Games & reports. We do not combine different results as if they were controlled tests.',
      recommended:'Recommended', experimental:'Experimental', compatibilitySpecific:'Compatibility / specific titles', communityReports:'Community-reported', documented:'Documented', sourceOnDocs:'Source: ShadowMountPlus documentation',
      researchLabel:'TRANSPARENCY', sourcesTitle:'Sources & methodology', sourcesIntro:'The starter set cross-references technical documentation, GitHub issues and public Reddit reports. Each game card links back to the source supporting its summary.', sourcesCountLabel:'sources indexed', lowConfidenceLabel:'reports with limited evidence', never:'Downloads', noDownloadsLabel:'we do not host games; links are for authorised files only',
      methodEvidenceTitle:'What does evidence quality mean?', methodEvidenceText:'<strong>High</strong>: detailed/reproducible issue or maintainer documentation. <strong>Medium</strong>: setup and result described with some detail. <strong>Low</strong>: short comment, missing fields or preliminary result. These labels describe documentation quality, not a statistical chance of success.',
      rulesTitle:'Editorial rules', rule1:'One report does not mean universal compatibility. Conflicting reports remain separate.', rule2:'“No issues so far” is a preliminary test; “game completed” covers more of the game.', rule3:'When firmware, format or storage is not stated, the Atlas marks it unknown rather than guessing.', rule4:'Historical lists of minimum/required game firmware are not mixed with runtime homebrew results.', rule5:'Summaries are paraphrases. Always open the original post for full context and later edits.',
      communityInput:'COMMUNITY CONTRIBUTIONS', contributeTitle:'Add a test result', contributeIntro:'Record an observation with enough context to help someone else.', formGameHeading:'Game and setup', formGameHint:'Only enter what you actually tested.', gameNameLabel:'Game title *', firmwareLabel:'Firmware *', consoleLabel:'Console', unknown:'Not stated', gameVersionLabel:'Game version', formatLabel2:'Format *', notSure:'Not sure / not stated', storageLabel:'Storage *', toolVersionsLabel:'Tool versions',
      formResultHeading:'Observed outcome', formResultHint:'Choose the closest outcome.', symptomsLabel:'Symptoms / notes *', symptomsPlaceholder:'What happened? How long did you test? Any error code?', resolutionLabel:'Resolution (if applicable)', resolutionPlaceholder:'What changed, and was it confirmed…', sourceUrlLabel:'Public post/issue URL *', consentText:'I confirm this is a result I observed or a public source I am citing; I have not included personal data.', saveReport:'Save locally', localOnly:'Submitted records stay in this browser only. They are not sent to a server.', formSaved:'Result saved in this browser only.',
      localPanelTitle:'Local contributions', localPanelText:'This prototype has no central backend. Export your records as JSON to review them or prepare a contribution to the repository.', localSaved:'records saved in this browser', exportJson:'Export JSON', clearLocal:'Delete local contributions', noLocalReports:'No local results saved yet.', confirmClear:'Delete all contributions saved in this browser?', localReport:'Local result', footerPreview:'Local preview · v0.2.0', footerNoAffiliation:'Independent community project. Not affiliated with Sony.', footerDocumentation:'Technical documentation ↗',
      sourceReports:'linked reports', publicCommunity:'Public community', maintainerDocs:'Maintainer documentation', openSourceList:'Open source ↗', exportDatabase:'Export dataset JSON', exportCsv:'Export reports CSV', copiedNoBackend:'The JSON was downloaded. Before adding reports to the public dataset, review the source and validate the fields.',
      status_playable_short:'Short / preliminary test', status_playable_issues:'Playable with issues', status_completed:'Completed with no issues reported', status_resolved:'Issue resolved in report', status_launch_failed:'Launch failure / black screen', status_crashes:'Crash / freeze', status_unknown:'Status unconfirmed', status_mixed:'Mixed reports',
      downloadsEyebrow:'OFFICIAL SOURCES · VERIFIABLE FILES', downloadsTitle:'Downloads & sources', downloadsIntro:'Browse homebrew published by its authors, inspect provenance, compare SHA-256 and manage a local download queue.', refreshCatalog:'Refresh catalogue ↻', downloadPolicyTitle:'Homebrew downloads with identified provenance', downloadPolicyText:'The Atlas links to official releases and reviewed homebrew catalogues. It checks hashes when a published value exists. It does not aggregate or distribute unauthorised copies of commercial games. External downloads may require opening the provider page.', catalogNotLoaded:'Catalogue not loaded. Click “Refresh catalogue”.', officialHomebrewCatalog:'Community homebrew catalogue', catalogExplanation:'Data from the community homebrew.page catalogue. Files are hosted by their projects, not by the Atlas.', homebrewSearchPlaceholder:'Search app, author or Title ID…', catalogPrompt:'Click the button to query the live catalogue.', otherOfficialTools:'Other homebrew projects', officialToolNote:'Official project pages. The Atlas does not import the game catalogues from these applications.', customSourcesTitle:'Custom sources', customSourcesIntro:'Save project or release pages you are authorised to use. Sources remain in your browser and are not published.', customSourceName:'Source name', customSourceUrl:'Project/release page URL', customSourceNamePlaceholder:'My authorized project', customSourceUrlPlaceholder:'https://github.com/author/project', customSourceConsentText:'I confirm that I am authorised to access and use the listed files, and I am not adding sources for unauthorised copies of commercial games.', saveCustomSource:'Save source locally', downloadQueueTitle:'Download queue', queueExplanation:'Compatible downloads are transferred in the browser and checked against the published SHA-256. If CORS or file size blocks direct transfer, open the official release.', startQueue:'Start queue', clearQueue:'Clear', queueEmpty:'The queue is empty.', sourceTypesTitle:'Source types', sourceVerified:'Published hash', sourceVerifiedText:'The file is compared with the catalogue SHA-256 before it can be saved.', sourceExternal:'External page', sourceExternalText:'Opens the provider’s official page; the Atlas does not bypass CAPTCHAs, authentication or temporary links.', sourceUnknown:'Unverified', sourceUnknownText:'Without a verifiable hash/origin, only the source page is shown; the file is not claimed to be safe.', privacyDownloadTitle:'Privacy and limitations', privacyDownloadText:'The queue and saved sources stay in this browser. The Atlas does not host files or receive logs. Direct downloads require CORS and browser memory; a size limit applies.', exportDownloadSettings:'Export sources and queue', importDownloadSettings:'Import saved sources',
    }
  };
  const memoryStorage = new Map();
  function storageGet(key, fallback='') { try { const v = window.localStorage.getItem(key); return v === null ? fallback : v; } catch { return memoryStorage.has(key) ? memoryStorage.get(key) : fallback; } }
  function storageSet(key, value) { try { window.localStorage.setItem(key, value); } catch { memoryStorage.set(key, String(value)); } }
  function storageRemove(key) { try { window.localStorage.removeItem(key); } catch { memoryStorage.delete(key); } }
  function sessionGet(key, fallback='') { try { const v = window.sessionStorage.getItem(key); return v === null ? fallback : v; } catch { return fallback; } }
  function sessionSet(key, value) { try { window.sessionStorage.setItem(key, value); } catch { /* Session-only preference can be skipped in restrictive browser contexts. */ } }
  let language = storageGet('ps5-atlas-language', 'pt') || 'pt';
  if (!I18N[language]) language = 'pt';
  let activeTab = 'games';
  let noticeDismissed = sessionGet('ps5-atlas-notice-dismissed') === '1';
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => [...root.querySelectorAll(sel)];
  const sourceMap = new Map(DATA.sources.map(s => [s.id, s]));
  const builtInReports = DATA.reports;
  const LOCAL_KEY = 'ps5-atlas-local-reports-v1';
  const fmtLabels = {
    folder:{pt:'Pasta / dump',en:'Folder / dump'}, ffpkg:{pt:'.ffpkg / UFS',en:'.ffpkg / UFS'}, exfat:{pt:'.exfat',en:'.exfat'},
    ffpfs:{pt:'.ffpfs / PFS',en:'.ffpfs / PFS'}, ffpfsc:{pt:'.ffpfsc / PFS container',en:'.ffpfsc / PFS container'},
    lz4:{pt:'LZ4',en:'LZ4'}, ps4fpkg:{pt:'PS4 Fake PKG',en:'PS4 Fake PKG'}
  };
  const statusClasses = {
    completed:'good', resolved:'fixed', playable_issues:'warn', playable_short:'neutral', launch_failed:'bad', crashes:'bad', mixed:'neutral', unknown:'neutral'
  };
  const statusI18n = {
    completed:'status_completed', resolved:'status_resolved', playable_issues:'status_playable_issues', playable_short:'status_playable_short', launch_failed:'status_launch_failed', crashes:'status_crashes', mixed:'status_mixed', unknown:'status_unknown'
  };

  function t(key) { return (I18N[language] && I18N[language][key]) || I18N.pt[key] || key; }
  function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }
  function applyLanguage() {
    document.documentElement.lang = language === 'pt' ? 'pt-PT' : 'en';
    $$('[data-i18n]').forEach(el => {
      const value = t(el.dataset.i18n);
      if (el.tagName === 'OPTION') el.textContent = value;
      else el.innerHTML = value;
    });
    $$('[data-i18n-placeholder]').forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
    $('#languageToggle').textContent = language === 'pt' ? 'EN' : 'PT';
    $('#dismissNotice').setAttribute('aria-label', language === 'pt' ? 'Fechar aviso' : 'Dismiss notice');
    $('#inputConsole').querySelectorAll('option[data-i18n]').forEach(opt => { opt.textContent = t(opt.dataset.i18n); });
    document.title = 'PS5 Game Compatibility Atlas';
    updateStats();
    renderGames();
    renderFormats();
    renderSources();
    renderLocalReports();
    window.dispatchEvent(new CustomEvent('atlas-language-change', {detail:{language}}));
  }
  function localReports() {
    try {
      const value = JSON.parse(storageGet(LOCAL_KEY, '[]'));
      return Array.isArray(value) ? value : [];
    } catch { return []; }
  }
  function saveLocalReports(items) { storageSet(LOCAL_KEY, JSON.stringify(items)); }
  function normalizeText(s) { return String(s ?? '').toLocaleLowerCase(language === 'pt' ? 'pt-PT' : 'en-US').normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function reportStatusLabel(status) { return t(statusI18n[status] || 'status_unknown'); }
  function reportQualityLabel(quality) { return t(quality === 'high' ? 'qualityHigh' : quality === 'medium' ? 'qualityMedium' : 'qualityLow'); }
  function statusChip(status, textOverride) {
    return `<span class="status-chip ${statusClasses[status] || 'neutral'}">${escapeHTML(textOverride || reportStatusLabel(status))}</span>`;
  }
  function formatLabel(value) {
    const normal = normalizeText(value);
    if (normal.includes('ffpfsc')) return fmtLabels.ffpfsc[language];
    if (normal.includes('ffpfs')) return fmtLabels.ffpfs[language];
    if (normal.includes('ffpkg') || normal.includes('ufs')) return fmtLabels.ffpkg[language];
    if (normal.includes('exfat')) return fmtLabels.exfat[language];
    if (normal.includes('lz4')) return fmtLabels.lz4[language];
    if (normal.includes('folder') || normal.includes('dump') || normal.includes('pasta')) return fmtLabels.folder[language];
    if (normal.includes('fake pkg')) return fmtLabels.ps4fpkg[language];
    return value;
  }
  function formatFilterMatch(formats, filter) {
    if (filter === 'all') return true;
    const all = normalizeText(formats.join(' '));
    const rules = {
      folder: /(folder|dump|pasta)/,
      ffpkg: /\.ffpkg|ffpkg|ufs/,
      exfat: /exfat/,
      ffpfs: /\.ffpfs(?!c)|ffpfs(?!c)/,
      ffpfsc: /ffpfsc/,
      lz4: /lz4/
    };
    return rules[filter] ? rules[filter].test(all) : true;
  }
  function storageFilterMatch(storages, filter) {
    if (filter === 'all') return true;
    const val = normalizeText(storages.join(' '));
    if (filter === 'internal') return val.includes('intern');
    if (filter === 'm2') return val.includes('m.2') || /\bm2\b/.test(val);
    if (filter === 'external-ssd') return val.includes('external ssd') || val.includes('ssd externo') || val.includes('nvme externo');
    if (filter === 'usb') return val.includes('usb') || val.includes('hdd externo') || val.includes('external hdd');
    return true;
  }
  function firmwareFilterMatch(fw, filter) {
    if (filter === 'all') return true;
    return String(fw || '').includes(filter);
  }
  function reportMatches(report) {
    const query = normalizeText($('#searchInput').value.trim());
    const fw = $('#firmwareFilter').value;
    const format = $('#formatFilter').value;
    const storage = $('#storageFilter').value;
    const status = $('#statusFilter').value;
    if (!firmwareFilterMatch(report.firmware, fw)) return false;
    if (!formatFilterMatch(report.formats || [], format)) return false;
    if (!storageFilterMatch(report.storage || [], storage)) return false;
    if (status !== 'all' && report.status !== status) return false;
    if (!query) return true;
    const searchable = [report.game, report.title_id, report.console, report.firmware, report.formats?.join(' '), report.storage?.join(' '), report.status,
      report.game_version, report.tools, report.summary_pt, report.summary_en, report.symptoms_pt, report.symptoms_en,
      report.resolution_pt, report.resolution_en, report.id].join(' ');
    return normalizeText(searchable).includes(query);
  }
  function groupReports(reports) {
    const grouped = new Map();
    reports.forEach(r => {
      const key = normalizeText(r.game);
      if (!grouped.has(key)) grouped.set(key, {game:r.game, reports:[]});
      grouped.get(key).reports.push(r);
    });
    const result = [...grouped.values()];
    const sort = $('#sortFilter').value;
    if (sort === 'alpha') result.sort((a,b) => a.game.localeCompare(b.game));
    else if (sort === 'problems') result.sort((a,b) => problemScore(b.reports) - problemScore(a.reports) || b.reports.length - a.reports.length || a.game.localeCompare(b.game));
    else result.sort((a,b) => b.reports.length - a.reports.length || a.game.localeCompare(b.game));
    return result;
  }
  function problemScore(reports) {
    return reports.reduce((sum,r) => sum + (['launch_failed','crashes'].includes(r.status) ? 3 : r.status === 'playable_issues' ? 2 : r.status === 'resolved' ? 1 : 0), 0);
  }
  function aggregate(reports) {
    const statuses = new Set(reports.map(r => r.status));
    const hasGood = [...statuses].some(s => ['completed','resolved'].includes(s));
    const hasBad = [...statuses].some(s => ['launch_failed','crashes','playable_issues'].includes(s));
    if (hasGood && hasBad) return {label:t('statusMixed'), kind:'mixed'};
    if (statuses.size > 1) return {label:t('statusMixed'), kind:'mixed'};
    const only = [...statuses][0] || 'unknown';
    const kind = only === 'completed' || only === 'resolved' ? 'good' : only === 'playable_issues' ? 'warn' : only === 'launch_failed' || only === 'crashes' ? 'bad' : 'neutral';
    return {label:reportStatusLabel(only), kind};
  }
  function qualityClass(q) { return q === 'high' ? 'high' : q === 'medium' ? 'medium' : 'low'; }
  function reportCard(report) {
    const source = sourceMap.get(report.source);
    const sourceLink = source ? `<a class="source-link" href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${t('openSource')}</a>` : '';
    const sourceLabel = source ? `${escapeHTML(source.publisher)} · ${escapeHTML(source.date)}` : t('sourceLabel');
    const summary = language === 'pt' ? report.summary_pt : report.summary_en;
    const resolution = language === 'pt' ? report.resolution_pt : report.resolution_en;
    const extent = language === 'pt' ? report.extent_pt : report.extent_en;
    const resUnknown = ['Não indicada.','Not reported.','No resolution was reported.'].includes(resolution);
    const formats = (report.formats || []).map(formatLabel).map(v=>`<span class="meta-chip">${escapeHTML(v)}</span>`).join('');
    const storages = (report.storage || []).map(s=>`<span class="meta-chip">${escapeHTML(s)}</span>`).join('');
    const tool = report.tools && !/Não indicadas \/ Not stated/i.test(report.tools) ? `<span class="meta-chip">${escapeHTML(report.tools)}</span>` : '';
    const gameVersion = report.game_version && !/Não indicada \/ Not stated/i.test(report.game_version) ? `<span class="meta-chip">${escapeHTML(report.game_version)}</span>` : '';
    const consoleInfo = report.console && !/Não indicado \/ Not stated/i.test(report.console) ? `<span class="meta-chip">${escapeHTML(report.console)}</span>` : '';
    const symptoms = language === 'pt' ? report.symptoms_pt : report.symptoms_en;
    const caveat = language === 'pt' ? report.note_pt : report.note_en;
    return `<article class="report-item">
      <div class="report-topline">${statusChip(report.status)}<span class="quality ${qualityClass(report.quality)}">${escapeHTML(reportQualityLabel(report.quality))}</span></div>
      <p class="report-summary">${escapeHTML(summary)}</p>
      <div class="report-meta"><span class="meta-chip">${escapeHTML(report.firmware || t('unknown'))}</span>${formats}${storages}${consoleInfo}${gameVersion}${tool}</div>
      ${symptoms ? `<p class="report-note">${escapeHTML(symptoms)}</p>` : ''}
      ${!resUnknown ? `<div class="report-resolution"><strong>${t('reportedResolution')}</strong>${escapeHTML(resolution)}</div>` : ''}
      ${caveat ? `<p class="report-caveat">${escapeHTML(caveat)}</p>` : ''}
      <div class="report-footer"><span class="report-note">${sourceLabel}</span>${sourceLink}</div>
      ${extent ? `<p class="report-note" style="margin-top:7px">${t('testScope')}: ${escapeHTML(extent)}</p>` : ''}
    </article>`;
  }
  function renderGames() {
    const filtered = builtInReports.filter(reportMatches);
    const groups = groupReports(filtered);
    $('#resultsGrid').innerHTML = groups.map(group => {
      const agg = aggregate(group.reports);
      const titleIds = [...new Set(group.reports.map(r=>r.title_id).filter(Boolean))];
      const gameSub = titleIds.length ? escapeHTML(titleIds.join(', ')) : t('noTitleId');
      const reportNoun = group.reports.length === 1 ? t('reportCountOne') : t('reportCountMany');
      return `<article class="game-card"><div class="game-card-header"><div><h3>${escapeHTML(group.game)}</h3><div class="game-subtitle">${gameSub}</div></div><span class="report-count">${group.reports.length} ${reportNoun}</span></div><div class="card-aggregate aggregate-${agg.kind}">${escapeHTML(agg.label)}</div>${group.reports.map(reportCard).join('')}</article>`;
    }).join('');
    $('#resultsHeading').textContent = `${groups.length} ${t('games')}`;
    $('#resultsSub').textContent = `· ${filtered.length} ${t('matchedConfigurations')}`;
    $('#emptyState').classList.toggle('hidden', groups.length > 0);
    $('#resultsGrid').classList.toggle('hidden', groups.length === 0);
    $('#tabReportCount').textContent = builtInReports.length;
  }
  function updateStats() {
    const uniqueGames = new Set(builtInReports.map(r=>normalizeText(r.game))).size;
    const positiveReports = builtInReports.filter(r => ['completed','resolved','playable_issues','playable_short'].includes(r.status)).length;
    $('#heroGameCount').textContent = uniqueGames;
    $('#metricGames').textContent = uniqueGames;
    $('#metricReports').textContent = builtInReports.length;
    $('#metricPlayable').textContent = positiveReports;
    $('#metricFormats').textContent = DATA.formats.length;
    $('#tabReportCount').textContent = builtInReports.length;
  }
  function stateLabelForFormat(fmt) {
    if (fmt.official_status === 'recommended') return {label:t('recommended'),kind:'recommended'};
    if (fmt.official_status === 'experimental') return {label:t('experimental'),kind:'experimental'};
    if (fmt.official_status === 'compatibility') return {label:t('compatibilitySpecific'),kind:'neutral'};
    if (fmt.official_status === 'community') return {label:t('communityReports'),kind:'neutral'};
    return {label:t('documented'),kind:'neutral'};
  }
  function renderFormats() {
    $('#formatsGrid').innerHTML = DATA.formats.map(fmt => {
      const state = stateLabelForFormat(fmt);
      const name = language === 'pt' ? fmt.label : fmt.label_en;
      const summary = language === 'pt' ? fmt.summary_pt : fmt.summary_en;
      const recommendation = language === 'pt' ? fmt.recommendation_pt : fmt.recommendation_en;
      const source = sourceMap.get(fmt.source);
      return `<article class="format-card"><div class="format-card-header"><div><h3>${escapeHTML(name)}</h3><div class="format-extension">${escapeHTML(fmt.extensions)}</div></div><span class="format-state ${state.kind}">${escapeHTML(state.label)}</span></div><p>${escapeHTML(summary)}</p><div class="format-recommendation"><strong>${language === 'pt' ? 'Nota prática' : 'Practical note'}:</strong> ${escapeHTML(recommendation)}</div>${source ? `<a class="format-source" href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${t('sourceOnDocs')} ↗</a>` : ''}</article>`;
    }).join('');
  }
  function renderSources() {
    $('#sourcesCount').textContent = DATA.sources.length;
    $('#lowConfidenceCount').textContent = builtInReports.filter(r=>r.quality==='low').length;
    $('#sourcesList').innerHTML = DATA.sources.map(source => {
      const note = language === 'pt' ? source.notes_pt : source.notes_en;
      const linked = builtInReports.filter(r=>r.source===source.id).length;
      const type = /Maintainer|documentation/i.test(source.type) ? t('maintainerDocs') : t('publicCommunity');
      return `<article class="source-card"><div class="source-card-top"><h3>${escapeHTML(source.title)}</h3><span class="source-type">${escapeHTML(source.type)}</span></div><div class="source-date">${escapeHTML(source.publisher)} · ${escapeHTML(source.date)}</div><p>${escapeHTML(note)}</p><div class="source-date">${linked} ${t('sourceReports')}</div><a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${t('openSourceList')}</a></article>`;
    }).join('');
    const intro = $('#view-sources .section-intro');
    if (!$('#exportDatabase')) {
      const button = document.createElement('button');
      button.id = 'exportDatabase'; button.className = 'control-button'; button.type = 'button';
      button.textContent = t('exportDatabase'); button.addEventListener('click', exportDatabase);
      intro.appendChild(button);
    } else $('#exportDatabase').textContent = t('exportDatabase');
    if (!$('#exportReportsCsv')) {
      const button = document.createElement('button');
      button.id = 'exportReportsCsv'; button.className = 'control-button'; button.type = 'button';
      button.textContent = t('exportCsv'); button.addEventListener('click', exportReportsCsv);
      intro.appendChild(button);
    } else $('#exportReportsCsv').textContent = t('exportCsv');
  }
  function downloadJson(name, value) {
    const blob = new Blob([JSON.stringify(value, null, 2)], {type:'application/json;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function exportDatabase() { downloadJson('ps5-game-compatibility-atlas-data.json', DATA); }
  function exportReportsCsv() {
    const fields = [
      ['id','ID'],['game','Game'],['title_id','Title ID'],['firmware','Firmware'],['console','Console'],['game_version','Game version'],
      ['formats','Formats'],['storage','Storage'],['status','Reported status'],['summary_pt','Summary PT-PT'],['summary_en','Summary EN'],
      ['symptoms_pt','Symptoms PT-PT'],['symptoms_en','Symptoms EN'],['resolution_pt','Resolution PT-PT'],['resolution_en','Resolution EN'],
      ['extent_pt','Test scope PT-PT'],['extent_en','Test scope EN'],['quality','Evidence quality'],['tools','Tools'],['note_pt','Caveat PT-PT'],
      ['note_en','Caveat EN'],['source','Source ID'],['source_title','Source title'],['source_type','Source type'],['source_date','Source date'],['source_url','Source URL']
    ];
    const cell = value => `"${(Array.isArray(value) ? value.join(' | ') : String(value ?? '')).replace(/"/g, '""')}"`;
    const lines = [fields.map(([,label]) => cell(label)).join(',')];
    builtInReports.forEach(report => {
      const source = sourceMap.get(report.source) || {};
      lines.push(fields.map(([key]) => {
        if (key === 'source_title') return cell(source.title || '');
        if (key === 'source_type') return cell(source.type || '');
        if (key === 'source_date') return cell(source.date || '');
        if (key === 'source_url') return cell(source.url || '');
        return cell(report[key]);
      }).join(','));
    });
    const blob = new Blob(['\ufeff' + lines.join('\r\n')], {type:'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'ps5-game-compatibility-atlas-reports.csv'; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function exportLocal() {
    const items = localReports();
    downloadJson('ps5-game-compatibility-atlas-local-reports.json', {schema_version:1, project:'PS5 Game Compatibility Atlas', exported_at:new Date().toISOString(), reports:items});
  }
  function renderLocalReports() {
    const items = localReports();
    $('#myReportCount').textContent = items.length;
    $('#localReportsTotal').textContent = items.length;
    if (!items.length) { $('#localReportsList').innerHTML = `<p class="report-note">${t('noLocalReports')}</p>`; return; }
    $('#localReportsList').innerHTML = items.slice().reverse().slice(0,8).map(item => `<div class="local-report-item"><strong>${escapeHTML(item.game)}</strong><span>${escapeHTML(item.firmware)} · ${escapeHTML(item.format)} · ${escapeHTML(item.created_at || '')}</span><span>${escapeHTML(reportStatusLabel(item.status))}</span></div>`).join('');
  }
  function switchTab(name) {
    activeTab = name;
    $$('.main-tab').forEach(btn => btn.classList.toggle('active', btn.dataset.tab === name));
    $$('.tab-view').forEach(view => view.classList.toggle('active', view.id === `view-${name}`));
    if (name === 'contribute') renderLocalReports();
  }
  function initializeFirmwareFilters() {
    const select = $('#firmwareFilter');
    const versions = ['13.60','13.40','13.20','13.00','12.70','12.00','11.60','11.40','10.01','7.61','6.00','4.03'];
    const options = versions.map(v => `<option value="${v}">${v}</option>`).join('');
    select.insertAdjacentHTML('beforeend', options);
  }
  function submitReport(event) {
    event.preventDefault();
    if (!$('#inputConsent').checked) return;
    const form = $('#reportForm');
    const values = Object.fromEntries(new FormData(form).entries());
    const sourceUrl = values.source_url.trim();
    try { const url = new URL(sourceUrl); if (!['http:','https:'].includes(url.protocol)) throw new Error('bad protocol'); }
    catch { $('#formFeedback').textContent = language === 'pt' ? 'Indica um endereço HTTPS/HTTP válido para a fonte pública.' : 'Enter a valid HTTP/HTTPS public source URL.'; $('#formFeedback').classList.remove('hidden'); return; }
    const record = {
      id:`LOCAL-${Date.now()}`, game:values.game.trim(), firmware:values.firmware.trim(), console:values.console || '', game_version:values.game_version?.trim() || '',
      format:values.format, storage:values.storage, tools:values.tools?.trim() || '', status:values.status, summary:values.summary.trim(), resolution:values.resolution?.trim() || '', source_url:sourceUrl, created_at:new Date().toISOString().slice(0,10)
    };
    const items = localReports(); items.push(record); saveLocalReports(items); form.reset();
    $('#formFeedback').textContent = t('formSaved'); $('#formFeedback').classList.remove('hidden');
    renderLocalReports();
  }
  function clearLocal() {
    if (!confirm(t('confirmClear'))) return;
    storageRemove(LOCAL_KEY); renderLocalReports();
  }

  // Initial state.
  initializeFirmwareFilters();
  if (noticeDismissed) $('.notice-bar').classList.add('hidden');
  $('#languageToggle').addEventListener('click', () => {
    language = language === 'pt' ? 'en' : 'pt'; storageSet('ps5-atlas-language', language); applyLanguage();
  });
  $('#dismissNotice').addEventListener('click', () => { $('.notice-bar').classList.add('hidden'); sessionSet('ps5-atlas-notice-dismissed','1'); });
  $$('.main-tab').forEach(btn => btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
  ['searchInput','firmwareFilter','formatFilter','storageFilter','statusFilter','sortFilter'].forEach(id => {
    const el = document.getElementById(id); el.addEventListener(id === 'searchInput' ? 'input' : 'change', renderGames);
  });
  $('#resetFilters').addEventListener('click', () => { $('#searchInput').value=''; $('#firmwareFilter').value='all'; $('#formatFilter').value='all'; $('#storageFilter').value='all'; $('#statusFilter').value='all'; $('#sortFilter').value='relevant'; renderGames(); });
  $('#emptyReset').addEventListener('click', () => $('#resetFilters').click());
  $('#reportForm').addEventListener('submit', submitReport);
  $('#exportLocalReports').addEventListener('click', exportLocal);
  $('#clearLocalReports').addEventListener('click', clearLocal);
  applyLanguage();
})();
