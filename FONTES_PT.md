# Fontes da base de conhecimento — PS5 Jailbreak Doctor

Revisão feita em 17-10-2026. A base contém 32 regras e 5 notas de compatibilidade nesta revisão. O repositório de issues muda com frequência; esta lista não significa que todos os casos continuem presentes nas versões mais recentes.

## ShadowMountPlus

- [#147 — TitleDir/AppInstallAll bridge indisponível após retomar do modo de repouso](https://github.com/drakmor/ShadowMountPlus/issues/147): caso específico de FW 13.40 e SM+ 1.7beta3. O mantenedor encerrou o issue em 10-10-2026 após adicionar um commit para restaurar os hooks antes do registo; confirmar se a build instalada contém a alteração.
- [#145 — o hook AppInstallAll perde-se após mudar de jogo](https://github.com/drakmor/ShadowMountPlus/issues/145): report semelhante, encerrado após o mesmo commit de recuperação dos hooks.
- [#109 — Failed to Install ShellCore Hooks](https://github.com/drakmor/ShadowMountPlus/issues/109): vários firmwares e versões beta; comportamento intermitente, sem solução confirmada.
- [#141 — registo com `0x80F50005`](https://github.com/drakmor/ShadowMountPlus/issues/141): título/versão específicos; não universalizar o código.
- [#56 — montagem `.ffpfsc` com `0x00000016 Invalid Argument`](https://github.com/drakmor/ShadowMountPlus/issues/56): relato antigo, versões antigas.
- [#66 — kernel panic com parênteses no nome `.ffpfs/.ffpfsc`](https://github.com/drakmor/ShadowMountPlus/issues/66): workaround de renomeação relatado num caso antigo.
- [#137 — comprimento máximo do nome do ficheiro](https://github.com/drakmor/ShadowMountPlus/issues/137): issue comunitária aberta sem limite numérico confirmado.
- [#136 — não encontra/monta jogos em `/data/homebrew`](https://github.com/drakmor/ShadowMountPlus/issues/136): relato de varrimento/caminhos.
- [#142 — jogos nem sempre montados automaticamente](https://github.com/drakmor/ShadowMountPlus/issues/142): recarregar o payload para voltar a varrer foi mencionado pelo utilizador; causa aberta.
- [#128 — jogo em pasta não relança, `CE-105773-3`](https://github.com/drakmor/ShadowMountPlus/issues/128): workaround com montagem manual funcionou num único caso em FW 13.60.
- [#32 — `image cache full, rolling back mount`](https://github.com/drakmor/ShadowMountPlus/issues/32): issue antiga, mostrou cache com 64 entradas e foi fechada após referência a um build de teste.
- [#127 — kernel panic ao mover jogo de `usb0` para `ext1`](https://github.com/drakmor/ShadowMountPlus/issues/127): caso de FW 13.60, SM+ 1.7beta4 e KStuff Lite 1.11.
- [#117 — LZ4 com SM+ 1.7beta2/KStuff Lite 1.11](https://github.com/drakmor/ShadowMountPlus/issues/117): combinação específica; o mantenedor comentou sobre `libkernel` nos backports. A app não aplica esse workaround.
- [#143 — `CE-108262-9` intermitente em PS4 fpkg](https://github.com/drakmor/ShadowMountPlus/issues/143): relato aberto, causa não isolada.
- [#150 — SIGSEGV/page fault durante cutscene](https://github.com/drakmor/ShadowMountPlus/issues/150): caso específico em FW 12.00/PS5 Pro e backport aplicado.
- [#135 — crash após backport, SIGBUS/INT 0x42](https://github.com/drakmor/ShadowMountPlus/issues/135): caso específico. Comentário sobre `Runtime`/`runtime` não é tratado como correção oficial e nenhuma permissão é alterada pela app.
- [#89 — “can't launch the game or app”](https://github.com/drakmor/ShadowMountPlus/issues/89): relato genérico antigo.
- [#22 — backports não aplicados](https://github.com/drakmor/ShadowMountPlus/issues/22): relato antigo, combinações de versões iniciais.
- [#97 — `0x80551618` ao registar troféus de jogos PS4 `.ffpfsc`](https://github.com/drakmor/ShadowMountPlus/issues/97): jogos montavam e eram jogáveis, mas o registo de troféus falhava.
- [#132 — acesso a `/preinst/common/font`](https://github.com/drakmor/ShadowMountPlus/issues/132): relato aberto específico de uma versão beta.
- [#140 — scan de FPKG instalados após reset](https://github.com/drakmor/ShadowMountPlus/issues/140) e [#149 — follow-up com problema ainda presente](https://github.com/drakmor/ShadowMountPlus/issues/149): relatos contraditórios; a app não recomenda editar `app.db`.
- [API do ShadowMountPlus 1.7](https://github.com/drakmor/ShadowMountPlus/blob/1.7/docs/api.md): referência para a integração de leitura.
- [README/documentação de troubleshooting do ShadowMountPlus 1.7](https://github.com/drakmor/ShadowMountPlus): suporte PFS é classificado como experimental; documentação descreve `scanpath`, `scan_depth`, `manual.lst`, estrutura de `sce_sys/param.json` e origens duplicadas por Title ID.
- Estado de compatibilidade de contexto revisto em 12-10-2026: a app só apresenta uma nota da matriz quando todos os campos definidos nessa entrada coincidem; os campos em falta não contam como confirmação.

## KStuff Lite e carregamento de payloads

- [Repositório KStuff Lite de drakmor](https://github.com/drakmor/kstuff-lite): documentação/código do payload; o próprio README descreve melhorias de validação e tratamento de crashes, mas não define um significado único para todo kernel panic.
- [#115 — instabilidade após atualização SM+ 1.6beta16 → 1.7beta1 e KStuff Lite 1.10 → 1.11](https://github.com/drakmor/ShadowMountPlus/issues/115): relatos de crashes e kernel panics sem atribuição definitiva a um componente.
- [#76 — jogos falham com KStuff Lite 1.07 beta + SM+](https://github.com/drakmor/ShadowMountPlus/issues/76): caso específico; utilizador indicou que voltar a uma versão anterior de KStuff resolveu o seu cenário.
- [Discussão de autoloader #14](https://github.com/itsPLK/ps5-y2jb-autoloader/discussions/14): relatos de crash ao carregar KStuff Lite 1.11 e crashes relacionados com estados de patches não oficiais de jogos PS4. O motor só usa isto como contexto de baixa confiança, não como prova causal.
- [Erro “App crashed before KStuff pause” (relato comunitário)](https://www.reddit.com/r/PS5_Jailbreak/comments/1trvz79/app_crashed_before_kstuff_pause/): experiência comunitária; não é diagnóstico oficial.

## Fontes acrescentadas na revisão de 17-10-2026

- [Release oficial ShadowMountPlus 1.7beta5](https://github.com/drakmor/ShadowMountPlus/releases/tag/1.7beta5): as notas anunciam recuperação automática dos hooks após retoma e antes do registo; a release removeu o pause automático antigo do KStuff e recomenda usar KStuff atualizado. É orientação da release, não prova da causa de cada crash.
- [#152 — listener HTTP/JSON deixa de aceitar ligações](https://github.com/drakmor/ShadowMountPlus/issues/152): reporta falha do listener na porta 10101 em 1.7-beta5fix1, enquanto outros serviços continuavam ativos. A causa exata não ficou confirmada na revisão.
- [#153 — scan permanece em fila após fechar jogo](https://github.com/drakmor/ShadowMountPlus/issues/153): reporta estado runtime preparado/montado que impede novas varreduras em FW 13.60 e 1.7-beta5fix1.
- [PR #163 — limitar a espera pela remoção do sandbox](https://github.com/drakmor/ShadowMountPlus/pull/163): proposta para limitar a espera; estava aberta na revisão de 17-10-2026 e não é tratada como correção já distribuída.
- [#128 — jogo em pasta falha ao voltar a iniciar](https://github.com/drakmor/ShadowMountPlus/issues/128): um relato em FW 13.60/1.7beta3 no qual a montagem manual permitiu iniciar novamente. Resultado de um sistema, com causa não confirmada.

## Como a app interpreta as fontes

1. **Documentação técnica**: descreve interfaces/formatos, não necessariamente a causa de um erro.
2. **Issue fechada**: pode estar resolvida numa build específica; verificar a versão antes de sugerir o workaround.
3. **Issue aberta/relato comunitário**: não é uma solução confirmada.
4. **Heurística**: associa uma assinatura a um significado plausível e pede contexto adicional.

A base é expansível, mas não pode prometer “todos os erros possíveis”: novos erros, firmware, payloads e builds podem mudar os sinais e as soluções. A aplicação não executa automaticamente qualquer operação de reparação.
