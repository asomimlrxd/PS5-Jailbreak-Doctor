"""Small offline PT-PT / English localization layer for the desktop UI."""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

LANGUAGE = "pt"
_TRANSLATIONS: dict[str, str] = {}
_PATCHED = False

# UI phrases are kept in Portuguese in the source and translated at widget creation.
UI_PT_EN = {
    "Diagnóstico local de logs da PS5 · ShadowMountPlus e KStuff Lite": "Local PS5 log diagnostics · ShadowMountPlus and KStuff Lite",
    "SHADOWMOUNTPLUS API": "SHADOWMOUNTPLUS API",
    "SESSÃO / ORIGENS": "SESSION / SOURCES",
    "Os dados desta sessão ficam no computador.": "Session data stays on this computer.",
    "Nenhuma origem carregada": "No sources loaded",
    "Ver logs completos": "View full logs",
    "Privacidade": "Privacy",
    "A análise é local. Os logs não são enviados automaticamente.": "Analysis is local. Logs are not uploaded automatically.",
    "ESTADO DA CONSOLA": "CONSOLE STATUS",
    "Versão da API: por confirmar": "API version: not confirmed",
    "Versão da API: ": "API version: ",
    "por confirmar": "not confirmed",
    "FERRAMENTAS": "TOOLS",
    "SOBRE O DIAGNÓSTICO": "ABOUT DIAGNOSTICS",
    "Os resultados são pistas baseadas nos logs e em referências públicas, não garantias de causa ou solução. A aplicação não executa correções na consola.": "Results are leads based on logs and public references, not guaranteed causes or fixes. The app does not apply fixes to the console.",
    "Os resultados são pistas, não causas confirmadas. A aplicação não altera a PS5.": "Results are leads, not confirmed causes. The app does not modify the PS5.",
    "Logs completos": "Full logs",
    "Texto original; não é modificado pela tradução da interface.": "Original text; it is not changed by interface translation.",
    "Ligação e segurança": "Connection & security",
    "LIGAÇÃO AO SHADOWMOUNTPLUS": "SHADOWMOUNTPLUS CONNECTION",
    "Indica o IP local da PS5 e a porta da API no painel superior. Testa a ligação antes de recolher os logs. A aplicação não modifica o config.ini nem altera a consola.": "Enter the PS5's local IP and API port in the top panel. Test the connection before fetching logs. The app does not modify config.ini or change the console.",
    "PRIVACIDADE E SEGURANÇA": "PRIVACY & SECURITY",
    "A API do ShadowMountPlus não tem autenticação nas versões suportadas. Utiliza-a apenas numa rede local de confiança e nunca encaminhes a porta para a Internet. Os logs são analisados localmente; não são enviados automaticamente.": "The ShadowMountPlus API has no authentication in the supported versions. Use it only on a trusted local network and never forward the port to the Internet. Logs are analyzed locally and are not uploaded automatically.",
    "Verificar scanner (leitura apenas)": "Inspect scanner (read-only)",
    "{count} origem(ns) · {line_count} linhas": "{count} source(s) · {line_count} lines",
    "origem(ns)": "source(s)",
    "Atualizar diagnósticos…": "Update diagnostics…",
    "linhas": "lines",
    "Ajuda a perceber erros em homebrew da PS5.": "Understand and troubleshoot PS5 homebrew issues.",
    "verificações locais": "local checks",
    "Obter logs da PS5": "Get PS5 logs",
    "Importar logs…": "Import logs…",
    "Ver exemplo fictício": "View demo example",
    "Analisar logs": "Analyze logs",
    "Mais opções ▾": "More options ▾",
    "Guardar relatório…": "Save report…",
    "Histórico e reversões…": "History & undo…",
    "Anonimizar relatório": "Anonymize report",
    "Limpar sessão": "Clear session",
    "Tema escuro": "Dark theme",
    "Tema claro": "Light theme",
    "Pronto para começar": "Ready to start",
    "Pronto — importa logs ou obtém os logs da PS5.": "Ready — import logs or get them from the PS5.",
    "PS5 não ligada": "PS5 not connected",
    "Resultado": "Results",
    "Logs": "Logs",
    "Ligação à PS5": "PS5 connection",
    "Os logs são analisados neste PC. A app não altera a consola.": "Logs are analyzed on this PC. The app does not modify the console.",
    "Resultado da análise": "Analysis results",
    "Abre um resultado para ver o que foi encontrado e os passos a seguir.": "Open a result to see what was found and what to do next.",
    "Detalhes técnicos (opcional) ▸": "Technical details (optional) ▸",
    "Ocultar detalhes técnicos ▾": "Hide technical details ▾",
    "Informação opcional para afinar o diagnóstico": "Optional information to refine the diagnosis",
    "Informação": "Information",
    "Firmware": "Firmware",
    "ShadowMountPlus": "ShadowMountPlus",
    "KStuff Lite": "KStuff Lite",
    "Formato": "Source format",
    "Onde está o jogo": "Game location",
    "Quando começou": "When it started",
    "Limpar": "Clear",
    "Estes dados só ajudam a comparar o teu caso com os relatos existentes.": "This information helps compare your case with existing reports.",
    "ERROS": "ERRORS",
    "AVISOS": "WARNINGS",
    "RESULTADO": "RESULTS",
    "Ainda não analisado": "Not analyzed yet",
    "Logs completos": "Full logs",
    "Importar ficheiros…": "Import files…",
    "Podes colar texto diretamente nesta área. Os logs ficam neste computador.": "You can paste text directly here. Logs stay on this computer.",
    "Ligar à PS5": "Connect to PS5",
    "Usa a API de leitura do ShadowMountPlus para obter automaticamente os logs mais recentes.": "Use the ShadowMountPlus read-only API to fetch the latest logs.",
    "ENDEREÇO DA CONSOLA": "CONSOLE ADDRESS",
    "IP da PS5": "PS5 IP address",
    "Porta": "Port",
    "Testar ligação": "Test connection",
    "Obter logs e analisar": "Get logs & analyze",
    "Ainda não ligado. Clica em «Testar ligação» para começar.": "Not connected yet. Click “Test connection” to begin.",
    "Privacidade e segurança": "Privacy & security",
    "A ligação só acontece quando carregas num botão. A API não tem autenticação: usa-a apenas numa rede local de confiança, nunca na Internet. Esta aplicação só lê a versão e os logs; não altera a consola.": "The app only connects when you click a button. The API has no authentication: use it only on a trusted local network, never on the Internet. This app only reads the version and logs; it does not modify the console.",
    "Ainda não há uma análise": "No analysis yet",
    "Começa por obter os logs da PS5 ou importar um ficheiro usando os botões acima. Também podes abrir um exemplo fictício para conhecer a aplicação; esse exemplo não representa a tua consola.\n\nQuando os logs estiverem carregados, escolhe ‘Analisar logs’. Depois abre um resultado para consultar as linhas encontradas e os passos sugeridos.": "Start by getting logs from the PS5 or importing a file using the buttons above. You can also open a demo example to explore the app; it does not represent your console.\n\nOnce the logs are loaded, choose ‘Analyze logs’. Then open a result to review the matching lines and suggested steps.",
    "A análise é feita neste computador. Nenhum ficheiro é enviado automaticamente.": "Analysis runs on this computer. No files are uploaded automatically.",
    "Logs e texto": "Logs and text files",
    "Todos os ficheiros": "All files",
    "Selecionar logs da PS5": "Select PS5 logs",
    "Não foi possível contactar a PS5": "Could not contact the PS5",
    "Ligação não estabelecida.": "Connection not established.",
    "Ligação confirmada": "Connection confirmed",
    "Ligação confirmada ✅": "Connection confirmed ✅",
    "✅ Ligação confirmada": "✅ Connection confirmed",
    "Agora clica em «Obter logs e analisar» para analisar os logs reais da PS5.": "Now click “Get logs & analyze” to analyze real PS5 logs.",
    "PS5 ligada": "PS5 connected",
    "✅ PS5 ligada": "✅ PS5 connected",
    "PS5: não ligada": "PS5: not connected",
    "❌ Não foi possível ligar. Confirma o IP, a porta e se a API está ativa.": "❌ Could not connect. Check the IP address, port, and whether the API is running.",
    "A PS5 não devolveu logs com conteúdo.": "The PS5 did not return any log content.",
    "Exemplo fictício carregado. Ao obter logs da PS5, este exemplo será substituído.": "Demo example loaded. It will be replaced when you fetch logs from the PS5.",
    "MODO DE DEMONSTRAÇÃO · Dados fictícios; não são logs da tua PS5.": "DEMO MODE · Sample data; these are not logs from your PS5.",
    "Origem: ainda não há logs carregados": "Source: no logs loaded yet",
    "ORIGEM: logs reais recolhidos da PS5 · o exemplo fictício foi descartado.": "SOURCE: real logs fetched from the PS5 · demo data was discarded.",
    "Logs limpos. Podes começar uma nova análise.": "Logs cleared. You can start a new analysis.",
    "Contexto limpo. Os logs continuam carregados.": "Context cleared. The logs are still loaded.",
    "A contactar a PS5 na rede local…": "Contacting the PS5 on the local network…",
    "A ligação expirou. Confirma o IP, a porta e se a API do ShadowMountPlus aceita ligações da rede local.": "The connection timed out. Check the IP address, port, and whether the ShadowMountPlus API accepts local-network connections.",
    "A PS5 recusou a ligação. Confirma que o ShadowMountPlus está ativo e que a API está configurada para aceitar ligações da LAN.": "The PS5 refused the connection. Check that ShadowMountPlus is running and that its API accepts LAN connections.",
    "A API respondeu, mas não autorizou o pedido. Confirma a versão e a configuração da API do ShadowMountPlus.": "The API responded but did not authorize the request. Check the ShadowMountPlus API version and configuration.",
    "Agora clica em «Obter logs e analisar» para analisar os logs reais da PS5.": "Now click “Get logs & analyze” to analyze real PS5 logs.",
    "Ainda não há logs": "No logs yet",
    "Importa um ficheiro, cola logs ou usa ‘Obter logs da PS5’. Depois carrega em ‘Iniciar diagnóstico’.": "Import a file, paste logs, or use ‘Get PS5 logs’. Then click ‘Analyze logs’.",
    "Não foram encontrados sinais de erro reconhecíveis": "No recognizable error signals were found",
    "Isto não garante que esteja tudo bem. Confirma se importaste o log certo e se inclui as linhas em redor do problema. Podes pesquisar termos como ‘error’, ‘failed’, ‘crash’, ‘panic’ ou voltar a recolher os logs depois de reproduzir o erro.": "This does not guarantee everything is fine. Check that you imported the correct log and included the lines around the issue. Look for terms such as ‘error’, ‘failed’, ‘crash’, or ‘panic’, or fetch the logs again after reproducing the issue.",
    "Abre um resultado para ver as linhas encontradas e os passos sugeridos. A análise não altera a consola.": "Open a result to view matching lines and suggested steps. Analysis does not modify the console.",
    "Fiabilidade estimada:": "Estimated confidence:",
    "Ver evidência e passos ▾": "View evidence & steps ▾",
    "Ocultar detalhes ▴": "Hide details ▴",
    "Identificador:": "Rule ID:",
    "Referência:": "Evidence type:",
    "Contexto:": "Context:",
    "Linha(s) encontrada(s)": "Matching log line(s)",
    "Orientação": "Guidance",
    "O que fazer a seguir": "What to do next",
    "Limites": "Limitations",
    "Referências:": "References:",
    "Abrir fonte ": "Open source ",
    "Ainda não há logs carregados": "No logs have been loaded yet",
    "Importa um ficheiro, cola logs ou usa ‘Obter logs da PS5’. Depois carrega em ‘Iniciar diagnóstico’.": "Import a file, paste logs, or use ‘Get PS5 logs’. Then click ‘Analyze logs’.",
    "Contexto divergente": "Context mismatch",
    "Contexto compatível": "Context matches",
    "Parcialmente compatível": "Partially matches",
    "Sem contexto": "No context provided",
    "Não necessário": "Not required",
    "Sem correspondência suficiente": "Not enough information to match",
    "Erro": "Error",
    "Aviso": "Warning",
    "Erro crítico": "Critical error",
    "Alta": "High",
    "Média": "Medium",
    "Baixa": "Low",
    "Heurística — precisa de contexto": "Heuristic — context needed",
    "Heurística baseada em relato comunitário": "Heuristic based on community report",
    "Documentação técnica": "Technical documentation",
    "Relato comunitário": "Community report",
    "Relato comunitário — questão aberta": "Community report — issue open",
    "Relato antigo/fechado — pode já ter mudado": "Old/closed report — may have changed",
    "Questão encerrada — pista específica do mantenedor": "Closed issue — maintainer-provided clue",
    "Relato comunitário genérico": "General community report",
    "Relato com alternativa não confirmada": "Report with unconfirmed workaround",
    "Relato comunitário antigo": "Older community report",
    "Vários relatos, causa não isolada": "Multiple reports; cause not isolated",
    "Relatos comunitários inconclusivos": "Inconclusive community reports",
    "Relatos abertos e contraditórios": "Open and conflicting reports",
    "Evento ainda não classificado": "Unclassified event",
    "Não necessário": "Not required",
    "Preenche o contexto opcional para confirmar se este caso corresponde ao cenário documentado.": "Fill in the optional context to check whether this case matches the documented scenario.",
    "O log corresponde à assinatura, mas o contexto informado diverge do cenário documentado (": "The log matches this signature, but the supplied context differs from the documented scenario (",
    "Trata esta hipótese como menos provável e não apliques o workaround específico sem confirmar os detalhes.": "Treat this as less likely and do not apply the specific workaround until the details are confirmed.",
    "Coincide em:": "Matches on:",
    "Ainda falta contexto para confirmar todos os critérios deste cenário.": "More context is needed to confirm all criteria for this scenario.",
    "Os dados fornecidos não permitem confirmar a aplicabilidade desta regra.": "The supplied information is not enough to confirm whether this rule applies.",
    "formato da origem": "source format",
    "armazenamento": "storage",
    "quando começou": "when it started",
    "versão do ShadowMountPlus": "ShadowMountPlus version",
    "versão do KStuff Lite": "KStuff Lite version",
    "Análise concluída:": "Analysis complete:",
    "resultado(s) · origem:": "result(s) · source:",
    ". A consola não foi alterada.": ". The console was not modified.",
    "O contexto não cria diagnósticos sozinho; pode reforçar ou reduzir a relevância de uma regra encontrada nos logs.": "Context does not create diagnoses by itself; it can increase or decrease the relevance of a rule found in the logs.",
    "Ainda não testado": "Not tested yet",
    "Em teste": "In progress",
    "Resolveu": "Resolved",
    "Não resolveu": "Not resolved",
    "Não apliquei": "Not applied",
    "Assistente de resolução — ": "Resolution assistant — ",
    "Verificação de contexto": "Context check",
    "Lista de verificação": "Checklist",
    "Antes de começar": "Before you begin",
    "Resumo": "Summary",
    "O progresso foi guardado localmente. Ainda não foi enviada nenhuma ação à PS5.": "Progress was saved locally. No action was sent to the PS5.",
    "Progresso guardado": "Progress saved",
    "Guardar progresso": "Save progress",
    "Notas (opcional)": "Notes (optional)",
    "Teste de nome reversível (opcional)": "Reversible filename test (optional)",
    "Escolher ficheiro e preparar teste…": "Choose file and prepare test…",
    "A aplicação só pode reverter os testes de nome que registou. Não sobrescreve o nome original se já existir um ficheiro com esse nome.": "The app can only undo filename tests that it recorded. It will not overwrite an existing file with the original name.",
    "Seleciona uma alteração para ver os caminhos e o estado.": "Select a change to view its paths and status.",
    "Renomeações reversíveis": "Reversible renames",
    "Planos de resolução": "Resolution plans",
    "Seleciona um plano para ver as notas.": "Select a plan to view notes.",
    "Sem notas.": "No notes.",
    "Reverter selecionada…": "Undo selected…",
    "Confirmar reversão": "Confirm undo",
    "Restaurar o nome original?\n\n": "Restore the original name?\n\n",
    "Reversão concluída": "Undo completed",
    "O nome original foi restaurado. O conteúdo não foi modificado.": "The original name was restored. The file contents were not modified.",
    "Não foi possível reverter": "Could not undo",
    "Não disponível": "Unavailable",
    "Esta ação já foi revertida ou não está disponível.": "This action has already been undone or is no longer available.",
    "Seleciona uma alteração": "Select a change",
    "Seleciona uma renomeação no histórico.": "Select a rename entry from the history.",
    "Sem logs": "No logs",
    "Importa ou cola logs antes de guardar um relatório.": "Import or paste logs before saving a report.",
    "Guardar relatório de diagnóstico": "Save diagnostic report",
    "Relatório Markdown": "Markdown report",
    "Ficheiro de texto": "Text file",
    "Erro ao guardar": "Save error",
    "Relatório guardado": "Report saved",
    "Confirma o conteúdo antes de o partilhares, mesmo com a anonimização ativada.": "Review the report before sharing it, even with anonymization enabled.",
    "Revê-o antes de o partilhares.": "Review it before sharing.",
    "Privacidade e segurança": "Privacy & security",
    "A app não vai alterar a PS5 pela API. Lê cada passo, confirma que corresponde ao teu caso e evita operações destrutivas. As referências comunitárias podem ser específicas de versões antigas.": "The app will not modify the PS5 through the API. Read each step, make sure it matches your case, and avoid destructive operations. Community reports may refer to older versions.",
    "O nome selecionado não corresponde": "The selected name does not match",
    "À espera dos logs": "Waiting for logs",
    " resultados para rever": " results to review",
    "1 resultado para rever": "1 result to review",
    "Confirmar teste reversível": "Confirm reversible test",
    "Escolhe a imagem PFS de origem": "Choose the source PFS image",
    "Fontes consultadas": "Sources consulted",
    "Histórico e reversão de alterações": "Change history & undo",
    "Indica o IP ou nome de anfitrião da PS5, sem caminho nem credenciais.": "Enter the PS5 IP address or hostname, without a path or credentials.",
    "Não foi possível guardar": "Could not save",
    "Não foi possível importar nenhum log.": "Could not import any logs.",
    "Não foi possível preparar o teste": "Could not prepare the test",
    "Os dados fornecidos não correspondem ao cenário documentado. Não vou preparar esta alteração.": "The supplied information does not match the documented scenario. This change will not be prepared.",
    "Só funciona com um ficheiro .ffpfs/.ffpfsc acessível ao Windows. A app altera apenas o nome local; não edita o conteúdo nem escreve na PS5. Para nomes com limite desconhecido, a sugestão é experimental.": "Works only with a .ffpfs/.ffpfsc file accessible to Windows. The app changes only the local filename; it does not edit the contents or write to the PS5. Suggestions for unknown filename limits are experimental.",
    "Relato comunitário — correção adicionada ao código após o relato": "Community report — a code fix was added after the report",
    "Relato aberto — causa ainda por confirmar": "Open report — root cause still unconfirmed",
    "Relato encerrado; confirmar se o build inclui a correção": "Closed report; confirm whether the installed build includes the fix",
    'É necessária uma versão mais recente da aplicação para esta base.': 'A newer application version is required for this database.',
    'Esta base requer a aplicação versão ': 'This database requires application version ',
    ' ou superior.': ' or later.',
    'A base não foi transferida. Atualiza primeiro a aplicação através do repositório oficial.': 'The database was not downloaded. Update the application first from the official repository.',
    'Erro ao procurar atualizações': 'Error checking for updates',
    'Falha na atualização': 'Update failed',
    'Atualização disponível': 'Update available',
    'Atualização concluída': 'Update complete',
    'Confirmar reversão': 'Confirm rollback',
    'Restaurar base de diagnósticos': 'Restore diagnostic database',
    'Reversão concluída': 'Rollback complete',
    'Não foi possível restaurar a base': 'Could not restore database',
    "Atualizar base de diagnósticos…": "Update diagnostic database…",
    "Reverter atualização da base…": "Restore previous diagnostic database…",
    "A verificar atualizações da base de diagnósticos…": "Checking diagnostic database updates…",
    "A base de diagnósticos já está atualizada.": "The diagnostic database is already up to date.",
    "Existe uma atualização da base de diagnósticos.": "A diagnostic database update is available.",
    "Queres transferir e instalar a versão ": "Would you like to download and install version ",
    "Alterações incluídas:": "Included changes:",
    "A transferir e validar a base de diagnósticos…": "Downloading and validating the diagnostic database…",
    "Base de diagnósticos atualizada para ": "Diagnostic database updated to ",
    "Atualização cancelada.": "Update cancelled.",
    "A procurar atualizações exige uma ligação à Internet. Os logs não são enviados.": "Checking for updates requires an internet connection. Logs are not uploaded.",
    "Não existe uma cópia de segurança válida para restaurar.": "There is no valid backup to restore.",
    "Queres restaurar a cópia de segurança da base de diagnósticos ": "Would you like to restore the diagnostic database backup ",
    "Base de diagnósticos restaurada para ": "Diagnostic database restored to ",
    "Verificar scanner": "Inspect scanner",
    "Esta aplicação só lê a versão, os logs e os detalhes do scanner; não altera a consola.": "This app only reads the version, logs, and scanner details; it does not modify the console.",
    "A API não devolveu uma resposta de versão válida.": "The API did not return a valid version response.",
    "A versão da API não anuncia leitura das definições do scanner.": "This API version does not advertise scanner settings reads.",
    "A versão da API não anuncia a lista de origens manuais.": "This API version does not advertise manual source listing.",
    "Não foi possível ler as definições do scanner.": "Could not read scanner settings.",
    "Não foi possível ler a lista de origens manuais.": "Could not read the manual source list.",
    "Definições do scanner": "Scanner settings",
    "Origens manuais": "Manual sources",
    "A versão instalada não disponibiliza os detalhes do scanner.": "The installed version does not expose scanner details.",
    "Estado do scanner — leitura apenas": "Scanner status — read-only",
    "Estado do scanner": "Scanner status",
    "Apenas leitura; não altera a consola.": "Read-only; does not modify the console.",
    "Raízes de varrimento personalizadas (scan_paths)": "Custom scan roots (scan_paths)",
    "A API não devolveu raízes personalizadas. Isto não significa que as raízes predefinidas estejam desativadas.": "The API returned no custom roots. This does not mean the default roots are disabled.",
    "Profundidade de varrimento (scan_depth)": "Scan depth (scan_depth)",
    "As definições do scanner não estão disponíveis nesta versão da API.": "Scanner settings are not available in this API version.",
    "Origens manuais (manual.lst)": "Manual sources (manual.lst)",
    "Origens listadas": "Listed sources",
    "A lista não contém origens manuais.": "No manual sources are listed.",
    "A lista de origens manuais não está disponível nesta versão da API.": "The manual source list is not available in this API version.",
    "Avisos": "Notes",
    "Nota: a API apresenta definições e origens manuais; esta consulta não executa uma nova varredura nem confirma que cada jogo pode ser iniciado.": "Note: the API reports settings and manual sources; this check does not run a new scan or confirm that each game can launch.",
    "Estado do scanner lido. Consulta o painel para veres os caminhos configurados.": "Scanner status read. Check the panel to view configured paths.",
    "Verificação do scanner concluída; não foram feitas alterações.": "Scanner check completed; no changes were made.",
    "Pré-verificação antes de alterar ficheiros": "Pre-flight checks before changing files",
    "Contexto técnico incompleto": "Incomplete technical context",
    "A aplicação não consegue comparar com rigor os relatos dependentes de versão sem estes dados: ": "The app cannot reliably compare version-specific reports without these details: ",
    "firmware": "firmware",
    "versão do ShadowMountPlus": "ShadowMountPlus version",
    "versão do KStuff Lite": "KStuff Lite version",
    "Preenche o firmware da PS5 e as versões exatas do ShadowMountPlus e KStuff Lite, se as conseguires confirmar.": "Fill in the PS5 firmware and exact ShadowMountPlus/KStuff Lite versions, if you can confirm them.",
    "Não assumes que um relato de outra versão se aplica ao teu caso.": "Do not assume a report from another version applies to your case.",
    "Pré-verificação do scanner e da origem": "Scanner and source pre-flight check",
    "Os logs incluem referências a scanpath, scan_depth, param.json ou a uma varredura sem resultados. Verifica a configuração e a estrutura antes de reinstalar ou apagar ficheiros.": "The logs mention scanpath, scan_depth, param.json, or a scan with no results. Check the configuration and source layout before reinstalling or deleting files.",
    "Confirma no debug.log quais as raízes de varrimento ativas e quantos jogos foram encontrados.": "Check debug.log for the active scan roots and the number of games found.",
    "Se existir uma linha scanpath= no config.ini, verifica se inclui a localização pretendida: raízes personalizadas podem substituir as raízes padrão.": "If config.ini contains a scanpath= line, check whether it includes the intended location: custom roots may replace the default roots.",
    "Confirma se scan_depth alcança o nível onde está a pasta do jogo e se sce_sys/param.json existe na raiz esperada.": "Check that scan_depth reaches the folder containing the game and that sce_sys/param.json exists at the expected root.",
    "Para origens fora das raízes de varrimento, consulta a documentação da build instalada sobre /data/shadowmount/manual.lst antes de editar a configuração.": "For sources outside the scan roots, check the documentation for your installed build about /data/shadowmount/manual.lst before editing the configuration.",
    "Ordem em que os sinais aparecem no ficheiro; isto não prova uma causa-raiz.": "Order in which signals appear in the file; this does not prove root cause.",
    "Cronologia de eventos": "Event timeline",
    "Sinal crítico": "Critical signal",
    "Linha": "Line",
    "Cronologia de erros (linhas do log)": "Error timeline (log lines)",
    "Linha ": "Line ",
    "Possível sinal crítico": "Possible critical signal",
    "Possível erro": "Possible error",
    "Aviso / estado": "Warning / state",
    "Notas de compatibilidade para o contexto indicado": "Compatibility notes for the supplied context",
    "Nota contextual": "Context note",
    "Estado da evidência: ": "Evidence status: ",
    "Nenhuma nota de compatibilidade corresponde a todas as versões e condições indicadas.": "No compatibility note matches all supplied versions and conditions.",
    "Resultado do diagnóstico": "Diagnostic outcome",
    "Não testado / Resolveu / Não resolveu": "Not tested / Resolved / Not resolved",
    "Passos que foram testados": "Steps that were tested",
    "Informação adicional": "Additional information",
    "Revê e anonimiza o relatório antes de o publicares.": "Review and anonymize the report before publishing it.",
    "Última revisão da base": "Knowledge base last reviewed",
    "Notas de compatibilidade": "Compatibility notes",
    "Estado da evidência": "Evidence status",
    "Acompanhamento após o teste (opcional)": "Follow-up after testing (optional)",
}

# English diagnostic text is kept outside the rule database so the database remains easy to edit.
RULE_EN = {
"SHADOW_TITLE_DIR": {
"title":"ShadowMountPlus: TitleDir bridge unavailable",
"summary":"ShadowMountPlus could not use the TitleDir/AppInstallAll interface or hook during registration/installation. One report describes the hook disappearing after resuming from rest mode. This message alone does not prove that game files are damaged.",
"steps":["Save the full debug.log and inspect the lines immediately before and after the warning.","If it started after resuming from rest mode, reload the ShadowMountPlus payload once. If it persists, perform a full restart and test again.","Confirm the exact firmware, ShadowMountPlus, and KStuff Lite versions. Note whether it happens after resume or also after a cold boot.","If it continues, share an anonymized report with the maintainer. Do not reinstall games as the first step."],
"fix_summary":"Reloading ShadowMountPlus after resume or performing a full restart is a recovery test, not a confirmed universal fix.",
"applicability":"Reports include FW 13.40/13.60 and ShadowMountPlus 1.7beta3; one case began after resuming from rest mode. This does not prove all cases have the same cause."},
"PRX_MODULE_LOAD": {
"title":"Failed to load a PRX module","summary":"The loader failed to load an application module. This message is generic and does not identify which module failed or why.",
"steps":["Record the Title ID, game version, and firmware the copy was prepared for.","Inspect the full logs for the PRX name immediately before the error.","Check the copy's structure and integrity, and confirm the files belong to the same version/region. Do not copy PRX files from another game.","Avoid removing files or changing backports until a log line points to a specific module."],
"fix_summary":"There is no universal fix. Find the first error before the crash and the module name mentioned.",
"applicability":"The code is generic; by itself it does not identify the failed PRX or the cause."},
"PARAM_JSON": {
"title":"Missing or invalid param.json","summary":"The scanner could not read the metadata expected for this title.",
"steps":["For a game folder, check whether sce_sys/param.json exists at the expected root.","For an image, check that sce_sys/param.json is at the image root, not inside an extra nested folder.","Open the JSON in a text editor and check that it is complete and syntactically valid. Keep a backup before editing."],
"fix_summary":"Check that sce_sys/param.json exists and is valid JSON at the expected root. Do not mix metadata from different versions.",
"applicability":"General rule; interpret it using the full context."},
"SOURCE_NOT_STABLE": {
"title":"Source is not stable yet","summary":"ShadowMountPlus detected that the source may still be copying, writing, or changing.",
"steps":["Confirm copying/extraction has finished and no program is writing to that folder or image.","Wait a few seconds and let the scanner check again.","If it happens with an unchanged source, save the log and review the stability/scanning settings supported by your version."],
"fix_summary":"Wait for copying/extraction to finish, close tools writing to the path, and scan again.",
"applicability":"General rule; interpret it using the full context."},
"KLOG_BUSY": {
"title":"Kernel log device is busy","summary":"The diagnostic component could not open /dev/klog because the system reported that the resource is busy.",
"steps":["The kernel log may not have been captured. Missing lines do not prove that no crash occurred.","Close duplicate diagnostic tools only, then retry once.","If it persists, include this message in the report and identify which payload/log server was active."],
"fix_summary":"Close duplicate log clients and retry once. A missing kernel log does not prove that no crash occurred.",
"applicability":"General rule; interpret it using the full context."},
"API_REFUSED": {
"title":"Connection refused by the PS5 local service","summary":"A TCP connection was refused. The service may not be running, may only be bound to localhost, or the address/port may be incorrect.",
"steps":["Confirm the expected payload/service is running and that the PS5 IP address has not changed.","For the ShadowMountPlus API, the documentation lists port 10101 and a default local bind of 127.0.0.1.","The API has no authentication: expose it to the LAN only if you trust the network, and never forward it to the Internet."],
"fix_summary":"Check the IP/port and whether the API accepts LAN connections. The API has no authentication; never expose it to the Internet.",
"applicability":"Connection between the PC and the ShadowMountPlus HTTP API."},
"APP_CRASH_BEFORE_KSTUFF": {
"title":"Application crashed before the KStuff pause","summary":"The diagnostic reports that the application crashed before KStuff reached the expected pause point.",
"steps":["Collect the full crash log and identify the Title ID and firmware version.","Compare against a known-compatible application and payload version. A log saying a backport was applied does not prove compatibility.","Look for the first error before the crash message; it is usually more useful than the final line."],
"fix_summary":"Compare the source format, payload version, and crash log. Do not change backports until there is a concrete clue.",
"applicability":"Reports involve different formats, firmwares, and versions; the message does not automatically mean KStuff is the cause."},
"MISSING_LIBC_PRX": {
"title":"libc.prx may be missing from the expected location","summary":"The log suggests that the application's module folder may not contain the expected PRX. Confirm the exact folder structure and full log line.",
"steps":["Check whether sce_module/libc.prx exists at the mounted application's root, when that title format requires it.","Confirm extraction/copying completed without errors and that the file belongs to the same game version.","Do not download or copy libc.prx from another title as a replacement."],
"fix_summary":"Check the path and integrity of the PRX belonging to the same title version; never copy libc.prx from another game.",
"applicability":"General rule; interpret it using the full context."},
"SHADOW_INSTALL_FAILURE": {
"title":"Generic ShadowMountPlus registration/installation failure","summary":"The log contains an installation or registration failure, but there is no more specific marker to establish the cause.",
"steps":["Read 20–40 lines before this event to find the first error.","Check the metadata and source path without removing the entry or deleting data.","Include the ShadowMountPlus version and an anonymized report when asking for help."],
"fix_summary":"The first error before the failure summary is usually more informative. Capture the exit code or [REG] line.",
"applicability":"General rule; interpret it using the full context."},
"SHADOW_SHELLCORE_HOOKS": {
"title":"ShadowMountPlus could not install ShellCore hooks","summary":"The payload reported a failure to install required ShellCore hooks. A public report describes this in different beta versions and says it was intermittent; the cause was not established.",
"steps":["Confirm the exact firmware, ShadowMountPlus, and KStuff Lite versions and save the full startup log.","Fully restart the console and load the payloads once, without repeatedly sending them.","If it continues, test a clean startup with as few payloads as possible, changing one variable at a time.","Do not replace system files or manually change offsets/hooks. Share the log with the maintainer."],
"fix_summary":"A full restart and clean-start test are diagnostic steps, not a confirmed solution.",
"applicability":"Reports include FW 11.60/12.70, ShadowMountPlus 1.7 alpha/beta, and KStuff Lite 1.11; do not generalize to all firmwares."},
"SHADOW_REG_80F50005": {
"title":"ShadowMountPlus: title registration failed (0x80F50005)","summary":"ShadowMountPlus recorded a failure in the AppInstallAll/REG process. A public report saw this code with one title while other games worked; that does not establish a universal cause or necessarily mean the image is corrupt.",
"steps":["Record the Title ID, format (folder/.exfat/.ffpfs/.ffpfsc), firmware, and ShadowMountPlus/KStuff Lite versions.","Check the log for ‘AppInstallAll bridge consumed’ and ‘[REG] FAIL’ to establish whether it failed during registration.","If only one title fails, compare that title's structure and param.json with the expected format. Collect logs before reinstalling anything.","Check whether the issue is known for your version; if it persists, attach an anonymized report to the maintainer's issue."],
"fix_summary":"There is no confirmed fix for all titles. Public evidence is specific to one game/version.",
"applicability":"Reported for FC 27 (PPSA34015), FW 12.00, ShadowMountPlus 1.7beta5Fix1, and experimental KStuff 1.13; the code may occur in other contexts."},
"SHADOW_MOUNT_INVALID_ARGUMENT_PFS": {
"title":"PFS mount rejected with Invalid Argument (0x00000016)","summary":"The PFS image mount failed with an invalid argument. A public case involved an .ffpfsc generated from an existing format and an older ShadowMountPlus version; the code may depend on format and version.",
"steps":["Confirm the extension, how the image was created, and whether your ShadowMountPlus version documents that format.","Test an intact copy of the same image without renaming it or rewriting its contents; record its hash and size.","If only one image fails, test it with the project's supported validation/creation tool and compare the full log."],
"fix_summary":"Confirm format compatibility and only recreate an image from an intact source if needed. There is no universal confirmed fix.",
"applicability":"Older report with FW 10.01, KStuff Lite 1.06, and ShadowMountPlus 1.6test15; applicability to 1.7 is uncertain."},
"SHADOW_PFS_PARENTHESES_PANIC": {
"title":"Possible PFS image filename bug involving parentheses","summary":"A kernel panic was reported when a .ffpfs/.ffpfsc filename containing parentheses was detected/mounted. Removing the parentheses resolved that specific case.",
"steps":["Only if the log and format match this exact scenario, disable auto-scan before renaming.","Rename only the source file to a short name without parentheses, keeping the extension; do not change its contents.","Test again and check whether the crash disappears. If the case does not match, do not assume the filename is the cause."],
"fix_summary":"Removing parentheses was reported to solve one older case. Do not modify the image contents, and keep a backup.",
"applicability":"Report with ShadowMountPlus 1.6test15-fix2 and FW 6.02; the issue is specific and may be fixed in newer versions."},
"SHADOW_FILENAME_TOO_LONG": {
"title":"Possible filename length limit","summary":"The community reported that long image filenames were not loaded by ShadowMount. The exact limit depends on the version and was not documented in the report.",
"steps":["Try a short test name that keeps the Title ID and extension, for example PPSA12345_Test.ffpfsc.","If the file is mounted or being scanned, pause the scanner before renaming it.","If the shorter name works, include the old/new names, extension, and version in the report."],
"fix_summary":"A shorter filename is a reversible test. Do not change the internal Title ID or the extension.",
"applicability":"Report from October 2026; the exact limit is still unspecified."},
"SHADOW_SCAN_MISSING_OR_AUTO_MOUNT": {
"title":"ShadowMountPlus scanner may not find/mount the source","summary":"Reports describe games missing from the scanner or appearing only after reloading the payload. Possible factors include configured paths, scan depth, format, or payload state.",
"steps":["Check scan_paths, scan_depth, and the number of games found in debug.log; confirm the folder is included.","Confirm the format/extension is supported by your version and that the filename/path is not over a known limit.","Try reloading the payload once to trigger a new scan; if it helps, save logs from before and after."],
"fix_summary":"Adjust paths only after confirming the active configuration. Reloading the payload is a reported workaround, not a guarantee.",
"applicability":"Several recent reports; the cause is not universal or confirmed."},
"SHADOW_FOLDER_GAME_RELAUNCH_CE1057733": {
"title":"Folder game will not mount again after exit (CE-105773-3)","summary":"A report on FW 13.60 describes a folder-format game that works on the first launch but fails after exiting and relaunching. The API showed mounted=false, and manually mounting through the official API UI restored launching in that case.",
"steps":["Confirm it is a folder-format title and that the error only appears on the second launch, after closing the game.","Check the installed/mounted status in the ShadowMountPlus UI; do not reinstall if the source is still available.","If manual mounting is available in your version, use the ShadowMountPlus UI. Do not run unknown API commands.","Attach the event timeline and debug.log to the maintainer's issue."],
"fix_summary":"Manual mounting worked in one published case; the same error may have another cause on other systems.",
"applicability":"Report on FW 13.60, KStuff Lite 1.11, and ShadowMountPlus 1.7beta3; observed on one system."},
"SHADOW_CACHE_FULL": {
"title":"ShadowMountPlus image cache is full","summary":"ShadowMountPlus aborted or rolled back a mount because it reported that the image cache was full. One report involved a library with over 100 images; this does not establish a universal limit.",
"steps":["Save the log and check how many entries it reports (for example, 64 in an older report).","Confirm you are using a current compatible ShadowMountPlus version; do not downgrade based only on an old report.","If the error recurs, temporarily reduce scanned sources using documented settings and test with a small library.","Do not manually delete the internal cache or delete games to free entries. Share the log if it persists."],
"fix_summary":"Reducing the number of scanned sources/images and checking for duplicates are safe operational tests; do not delete the internal cache manually.",
"applicability":"Report on FW 10.01, ShadowMountPlus 1.6test11, and KStuff 1.6.7; the log showed 64 entries. The maintainer linked a test build, so the limit/bug may have changed in later versions."},
"SHADOW_MOVE_FOLDER_KP": {
"title":"Kernel panic when moving a game between USB and ext1 storage","summary":"A kernel panic was reported when moving a game folder from /mnt/usb0 to ext1 with ShadowMountPlus 1.7beta4 and KStuff Lite 1.11 on FW 13.60.",
"steps":["Do not repeat the move operation with the same version if your scenario matches the report.","Confirm you have a backup and keep the original files intact.","Use an alternative copy method that does not call ShadowMountPlus's Move routine; validate sizes and hashes before deleting the source.","Report the log and transfer direction to the maintainer."],
"fix_summary":"Temporarily avoiding the integrated Move function is the safest option for this scenario; the cause remains unconfirmed.",
"applicability":"Open report for FW 13.60, ShadowMountPlus 1.7beta4, and KStuff Lite 1.11."},
"KSTUFF_SM_LZ4_BACKPORT_CONFLICT": {
"title":"Possible compatibility issue: KStuff Lite 1.11, ShadowMountPlus 1.7beta2, and LZ4 images","summary":"A public case reported LZ4 images stopped working with KStuff Lite 1.11 and ShadowMountPlus 1.7beta2. The maintainer commented about removing libkernel from backports. This is not a recommendation to change any backport without confirming the exact case.",
"steps":["Confirm all three version/format conditions exactly match the report before taking action.","Back up the full game and its backport directory before any edit.","Compare with versions recommended in current project releases/issues.","Do not remove libkernel or change backports automatically; follow the maintainer's current guidance for the exact game."],
"fix_summary":"The issue suggests a backport/libkernel interaction in one specific case. The app must not modify backports automatically.",
"applicability":"Report on FW 12.02, KStuff Lite 1.11, ShadowMountPlus 1.7beta2, and LZ4 images."},
"SHADOW_GAME_CANNOT_LAUNCH": {
"title":"PS5 cannot launch the mounted application","summary":"The source may have mounted/registered successfully while the system still fails to start the title. The reports are broad and do not identify a single cause.",
"steps":["Look for the first failure before the launch message in debug.log; distinguish mounting, registration, and startup crashes.","Check whether it affects one title or several, and record the image type and payload versions.","Do not assume reinstalling or changing firmware will help; preserve the source and compare with a working title."],
"fix_summary":"There is no universal fix; the first preceding error is needed for a more precise hypothesis.",
"applicability":"Older report on FW 9.00; broad and potentially version-dependent."},
"SHADOW_PS4_CE1082629": {
"title":"Intermittent CE-108262-9 when running PS4 fpkg games","summary":"An intermittent CE-108262-9 error was reported in PS4 fpkg games on the internal SSD with a particular payload combination; the author did not establish the cause. This is different from a confirmed corrupt-image diagnosis.",
"steps":["Record whether it happens only in PS4 fpkg games or also PS5 games, and at what stage.","Save the log, all payload versions, and firmware; compare the same operation after a full restart.","Do not blame KStuff or ShadowMountPlus without a controlled test that changes one variable at a time."],
"fix_summary":"No confirmed fix in the referenced issue; collect context and compare versions.",
"applicability":"Report on FW 13.60 and ShadowMountPlus 1.7beta3; intermittent error, cause unknown."},
"KSTUFF_SM_UPDATE_CRASHES": {
"title":"Crashes or kernel panics after updating KStuff Lite/ShadowMountPlus","summary":"Reports describe increased instability after updating KStuff Lite and ShadowMountPlus together, including failures when entering rest mode, closing games, or launching certain formats. The reports do not always isolate the cause.",
"steps":["Record exact versions before and after the update and confirm the PS5 was fully restarted afterward.","Avoid updating several payloads at once; use stable/compatible releases documented by the maintainers.","If the problem began immediately after updating, compare versions against project documentation and keep a configuration backup.","Do not downgrade to random or firmware-incompatible payloads; follow a version explicitly recommended by the maintainer."],
"fix_summary":"A full restart after updates and testing one variable at a time are prudent steps, not a definitive diagnosis.",
"applicability":"Reports involve several versions/firmwares; this broad match is not enough to blame a component."},
"SHADOW_SIGSEGV_IN_GAME": {
"title":"Game process crashed with SIGSEGV/page fault","summary":"The game process terminated because of a memory fault. In some reports, mounting and registration succeeded and the game crashed only during a cutscene or after a backport was applied; this does not prove ShadowMountPlus or KStuff caused it.",
"steps":["Identify the Title ID, crash timing, applied backport, firmware, and payload versions.","Look for thread name, fault address, RIP, and backtrace; save the kernel capture/core if available.","Compare with the same image/format in another method only if you already have it and it is safe; do not change modules/backports based only on SIGSEGV.","If it happens immediately after ‘Backport applied’, treat game/backport compatibility as a hypothesis, not a fact."],
"fix_summary":"There is no universal fix. The crash log and game context are needed to distinguish a game, backport, or environment issue.",
"applicability":"Public cases involve specific titles and firmwares; SIGSEGV alone is a generic signature."},
"SHADOW_BACKPORT_RUNTIME_CASE": {
"title":"Immediate crash after applying a backport (SIGBUS/int 0x42)","summary":"A public issue describes an immediate crash after applying a backport, with SIGBUS/INT 0x42, even after testing some fakelib settings. A user comment suggests checking the capitalization of the Runtime folder, but this was not validated by the maintainer.",
"steps":["Confirm the log includes SIGBUS/int 0x42 and that the crash happens immediately after the backport is applied.","Confirm the game folder structure and names match the documentation for that version; do not rename them automatically.","Make a full backup before any change. Do not run recursive chmod on all of /data/homebrew or change the global fakelib as a first test.","Attach debug.log and kernel capture to the specific issue for confirmation."],
"fix_summary":"The Runtime/runtime suggestion was not officially confirmed. Verify the structure and ask for validation; no automatic changes.",
"applicability":"Report on a specific game, FW 13.60, ShadowMountPlus 1.7beta3/beta4, and KStuff Lite 1.11; Runtime/runtime was suggested by a user."},
"KSTUFF_LOAD_KERNEL_PANIC": {
"title":"Kernel panic/crash associated with loading KStuff Lite","summary":"The community reported crashes/reboots after loading KStuff Lite with some firmware, exploit/loader, and payload combinations. These reports do not always isolate the cause; it may be version conflict, loading order, or another console state.",
"steps":["Confirm firmware and exact KStuff Lite version; save the debug message and the point where the crash occurred.","After updating payloads, fully restart before testing again.","Test only the minimum required set and change one variable at a time; do not repeatedly load the payload after a crash.","If the problem began after installing unofficial patches for PS4 games, record that as a possible diagnostic variable. Do not delete games or rebuild the database automatically."],
"fix_summary":"A full restart after updates and controlled payload/version testing are diagnostic steps. There is no universal confirmed fix.",
"applicability":"Reports involve different versions and firmwares; the crash may occur before or after ShadowMountPlus and does not prove KStuff Lite is the cause."},
"SHADOW_BACKPORT_NOT_APPLYING": {
"title":"Backport may not be applied / game will not start","summary":"Reports describe folder-format titles failing on older firmwares even with a ‘backports’ folder beside the source. An older issue used early ShadowMountPlus and KStuff Lite versions, so relevance depends on the current version and exact folder layout.",
"steps":["Confirm the backport matches the exact Title ID and game version, not just a similarly named title.","Check debug.log for an explicit message that the backport was applied; a notification alone does not prove compatibility.","Confirm the folder layout and documented options for the installed version. Back up before changing anything.","Do not copy libraries from another game or edit the executable to try to fix the failure."],
"fix_summary":"There is no universal confirmed solution; verify the backport match and logs first.",
"applicability":"Older report: FW 4.03, ShadowMountPlus 1.6beta9, KStuff Lite 1.03, folder-format game; it does not guarantee behavior on version 1.7."},
"SHADOW_TROPHY_REG_80551618": {
"title":"Trophy registration failed for a PS4 .ffpfsc game (0x80551618)","summary":"A trophy registration error was reported in PS4 games mounted from .ffpfsc even though they mounted and were playable. The report describes a difference between generic mounting and the normal PS4 install/launch path; no general fix has been confirmed.",
"steps":["Confirm this happens with a PS4 game using .ffpfsc, not a PS5 game or another format.","Save debug.log and record how the .ffpfsc was created, plus ShadowMountPlus version and firmware.","Do not rebuild the entire library or change trophy files; the reported issue may be system registration rather than the image.","Check the maintainer's issue before changing the method or format."],
"fix_summary":"No universal fix is confirmed in the referenced issue; preserve the image and collect versions/logs.",
"applicability":"Report from July 2026 on PS4 games converted from PKG to .ffpfsc; do not generalize to other formats."},
"SHADOW_SCAN_INSTALLED_FPKG_AFTER_RESET": {
"title":"ShadowMountPlus no longer detects some installed FPKGs after reset/restart","summary":"Reports describe ShadowMountPlus no longer detecting some installed FPKGs after a reset/restart, apparently involving indexing/app.db. A follow-up says the original case was not fixed in beta5fix1, so the state and solution may vary by version.",
"steps":["Confirm whether the title worked before the reset and whether only installed FPKGs are affected, or also folder/image-mounted games.","Save debug.log, ShadowMountPlus version, and the reset timing; look for [DB], [SCAN], app.db, and app.pkg lines.","Do not rebuild the database again or manually edit app.db as a first step; the original report tried safe-mode operations without a confirmed fix.","Check issues #140/#149 for your version and report the IDs of titles no longer detected."],
"fix_summary":"No universal confirmed fix in the referenced sources. Do not edit or manually delete the database.",
"applicability":"Reports involve ShadowMountPlus beta4/beta5fix1 and FW 10.01; the issue was closed and later reopened in a user follow-up."},
"SHADOW_PREINST_FONT_ACCESS": {
"title":"Mounted game cannot access /preinst/common/font","summary":"An open issue describes mounted games failing to access /preinst/common/font in ShadowMountPlus 1.7beta4. A path line alone does not prove a problem; an access error must appear in the same log.",
"steps":["Confirm the line reports an access failure, not just a successful mount of that path.","Record firmware, ShadowMountPlus version, and whether the title uses folder or image format.","Do not copy system fonts into the game or change global permissions.","If it persists, attach the relevant excerpt and debug.log to the maintainer's issue."],
"fix_summary":"No general fix is confirmed. Confirm the log shows a real access failure before taking action.",
"applicability":"Open report from October 2026 for ShadowMountPlus 1.7beta4; not a universal cause."},
"SHADOW_DUPLICATE_TITLE_ID": {
"title":"Duplicate Title ID detected across sources",
"summary":"ShadowMountPlus reports that more than one source maps to the same Title ID. Duplicate sources can make scanning and mounting ambiguous; the notification does not mean either source is corrupt.",
"steps":["Record the Title ID and list the folders/images that contain the same title.", "Keep one active source per Title ID in the scanned locations, following the current ShadowMountPlus documentation. Do not delete originals as the first step.", "If a source is outside the normal scan roots, check the documented manual.lst option and verify the exact path before changing configuration.", "Rescan and review debug.log. If the warning persists with one source, share an anonymized report and the relevant version information."],
"fix_summary":"Identify duplicate sources for the same Title ID and keep only one active source in the scan set; preserve a backup before removing or moving files.",
"applicability":"Based on the ShadowMountPlus 1.7 troubleshooting documentation; behavior can differ by version and source layout."},
}

# More app-specific short phrases and messages.
UI_PT_EN.update({
    "Origem: ": "Source: ",
    " ficheiro(s) importado(s) do computador.": " file(s) imported from this computer.",
    "Importados ": "Imported ",
    " ficheiro(s).": " file(s).",
    " Alguns falharam: ": " Some failed: ",
    "Recolhidos ": "Fetched ",
    " log(s) da PS5. Os dados anteriores foram substituídos.": " PS5 log(s). Previous data was replaced.",
    " ficheiro(s) de log. Clica em «Resultado» para ver a análise.": " log file(s). Click “Results” to view the analysis.",
    "ORIGEM: ": "SOURCE: ",
    " logs reais recolhidos da PS5 · o exemplo fictício foi descartado.": " real logs fetched from the PS5 · demo data was discarded.",
    " resultado(s)": " result(s)",
    "Análise concluída: ": "Analysis complete: ",
    " · origem: ": " · source: ",
    ". A consola não foi alterada.": ". The console was not modified.",
    "Não foi possível ligar. Confirma o IP, a porta e se a API está ativa.": "Could not connect. Check the IP, port, and whether the API is running.",
    "O progresso não foi guardado: ": "Progress was not saved: ",
    "Progresso guardado: ": "Progress saved: ",
    "Relatório guardado: ": "Report saved: ",
    "Teste reversível preparado: ": "Reversible test prepared: ",
    "Nome anterior:\n": "Previous name:\n",
    "Novo nome:\n": "New name:\n",
    "A app vai alterar APENAS o nome deste ficheiro no Windows; não altera o conteúdo.\n\nAntes de continuar, confirma que:\n• escolheste a origem exata mencionada no log;\n• o ShadowMountPlus deixou de examinar/montar esse ficheiro;\n• aceitas o teste comunitário (não é uma correção garantida).\n\nA operação ficará registada em Histórico / Reverter. Continuar?": "The app will change ONLY this file's name in Windows; it will not change its contents.\n\nBefore continuing, confirm that:\n• you selected the exact source mentioned in the log;\n• ShadowMountPlus has stopped scanning/mounting this file;\n• you accept this community-reported test (it is not a guaranteed fix).\n\nThe operation will be recorded in History & undo. Continue?",
    "O conteúdo do ficheiro não foi alterado. Se o teste não ajudar, abre ‘Histórico / Reverter…’ para restaurar o nome original.": "The file contents were not changed. If the test does not help, open ‘History & undo…’ to restore the original name.",
    "O progresso não foi guardado": "Progress was not saved",
    "A aplicação não vai alterar a PS5 pela API.": "The app will not modify the PS5 through the API.",
    "✅ Logs recebidos. Foram obtidos ": "✅ Logs received. ",
    " ficheiro(s) de log. Clica em «Resultado» para ver a análise.": " log file(s) received. Click “Results” to view the analysis.",
    "Ao copiar/mover ficheiros": "During file copy/move",
    "Ao iniciar o jogo": "When launching a game",
    "Apenas num jogo": "One title only",
    "Em vários jogos": "Multiple titles",
    "Após atualizar payload/ferramenta": "After a payload/tool update",
    "Após modo de repouso": "After rest mode",
    "Após sair do jogo": "After closing a game",
    "Pasta de jogo": "Game folder",
    "Resultado do teste": "Test result",
    "Progresso guardado no computador. Estes registos são notas locais; não indicam que a app tenha executado uma correção na PS5.": "Progress saved on this computer. These are local notes; they do not mean the app applied a fix to the PS5.",
    "Acompanhar resolução passo a passo…": "Guided troubleshooting…",
    "Título já instalado": "Installed title",
})

# Additional UI and runtime-error phrases found during the English-language audit.
# Keep user-facing exceptions localized too; internal identifiers and log contents are
# intentionally left untouched.
UI_PT_EN.update({
    "Avisos: ": "Warnings: ",
    "Falha no endpoint de versão: ": "Version endpoint failed: ",
    "A API respondeu com erro: ": "The API returned an error: ",
    "Teste preparado": "Test prepared",
    "Estado: ": "Status: ",
    " · passos concluídos: ": " · steps completed: ",
    "Nome alterado": "Renamed",
    "Revertido": "Reverted",
    "A porta tem de estar entre 1 e 65535.": "The port must be between 1 and 65535.",
    "Não foi possível encontrar um nome de destino livre.": "Could not find an available destination name.",
    "Esta regra não tem uma ação local reversível associada.": "This rule has no associated reversible local action.",
    "Esta regra não disponibiliza uma renomeação assistida.": "This rule does not support an assisted rename.",
    "O ficheiro selecionado não existe ou não é um ficheiro normal.": "The selected file does not exist or is not a regular file.",
    "Por segurança, não renomeio links simbólicos.": "For safety, symbolic links are not renamed.",
    "Seleciona o ficheiro numa unidade local. Caminhos de rede não são suportados neste teste.": "Select a file on a local drive. Network paths are not supported for this test.",
    "Seleciona um ficheiro .ffpfs ou .ffpfsc. A extensão não será alterada.": "Select a .ffpfs or .ffpfsc file. The extension will not be changed.",
    "O nome selecionado não contém parênteses; não corresponde ao cenário desta regra.": "The selected name does not contain parentheses, so it does not match this rule's scenario.",
    "Este nome tem menos de 60 caracteres. Como o limite exato não está documentado, a app não vai sugerir uma renomeação automática para este caso.": "This name is shorter than 60 characters. Since the exact limit is undocumented, the app will not suggest an automatic rename for this case.",
    "O nome proposto é igual ao atual; não há alteração a fazer.": "The proposed name matches the current name; there is nothing to change.",
    "A alteração não existe no histórico.": "The change does not exist in the history.",
    "Esta alteração já foi revertida ou não está disponível para reversão.": "This change has already been undone or is no longer available to undo.",
    "O ficheiro renomeado não foi encontrado. Liga a unidade onde está guardado e tenta novamente.": "The renamed file could not be found. Connect the drive where it is stored and try again.",
    "Já existe um ficheiro com o nome original. Não vou substituir ficheiros durante a reversão.": "A file with the original name already exists. Files will not be overwritten during undo.",
    "O ficheiro parece ter sido modificado após a renomeação. A reversão automática foi bloqueada para evitar perder dados.": "The file appears to have changed after it was renamed. Automatic undo was blocked to prevent data loss.",
    "Schema da base de conhecimento inválido.": "The knowledge-base schema is invalid.",
    "Campos compatíveis com o relato/documentação: ": "Fields matching the report/documentation: ",
    ". Isto reforça a relevância, mas não prova a causa.": ". This increases relevance, but does not prove the cause.",
    "Eventos de erro ainda não classificados": "Unclassified error events",
    "Encontrei linhas com termos de erro/crash que não foram explicadas pelas regras atuais. A base é incompleta por definição: usa estas linhas para acrescentar uma regra nova, sem assumir uma causa.": "I found lines containing error/crash terms that are not explained by the current rules. The database is inherently incomplete: use these lines to add a new rule without assuming a cause.",
    "Lê 20–40 linhas antes do primeiro evento e procura a primeira falha, não apenas a última mensagem.": "Read 20–40 lines before the first event and look for the first failure, not just the final message.",
    "Confirma firmware, versões de KStuff Lite e ShadowMountPlus, tipo de origem e Title ID.": "Confirm the firmware, KStuff Lite and ShadowMountPlus versions, source type, and Title ID.",
    "Guarda o relatório anonimizado e compara com o repositório de issues do projeto correspondente.": "Save the anonymized report and compare it with the relevant project's issue tracker.",
    "Não executes comandos, alteres permissões ou apagues ficheiros só por esta classificação genérica.": "Do not run commands, change permissions, or delete files based only on this generic classification.",
    "Ainda não há uma correção segura associada a estas linhas; é necessária triagem.": "No safe fix is associated with these lines yet; further triage is needed.",
    "a API não devolveu texto de log reconhecível.": "the API returned no recognizable log text.",
    " · Confiança: ": " · Confidence: ",
    "contexto divergente": "context mismatch",
    "Alta para o significado; baixa para a causa": "High for the meaning; low for the cause",
    "Alta para a mensagem; baixa para a causa subjacente": "High for the message; low for the underlying cause",
    "Alta para a mensagem; causa desconhecida": "High for the message; cause unknown",
    "Alta para o crash; baixa para a causa": "High for the crash; low for the cause",
    "Alta para o registo falhado; baixa para a causa": "High for the failed registration; low for the cause",
    "Baixa a média": "Low to medium",
    "Não apliques já o workaround específico desta regra: o contexto escolhido não corresponde ao cenário registado. Confirma o formato, as versões e quando começou o erro.": "Do not apply this rule's specific workaround yet: the selected context does not match the recorded scenario. Confirm the format, versions, and when the error started.",
    "# PS5 Jailbreak Doctor — Relatório de diagnóstico": "# PS5 Jailbreak Doctor — Diagnostic Report",
    "Versão da ferramenta": "Tool version",
    "Base de conhecimento": "Knowledge base",
    "regras locais": "local rules",
    "Método": "Method",
    "regras locais; sem envio automático de dados.": "local rules; no data is uploaded automatically.",
    "Anonimização de caminhos/IP": "Path/IP anonymization",
    "ativada": "enabled",
    "desativada": "disabled",
    "Fontes carregadas": "Loaded sources",
    "texto manual / não especificado": "manual text / unspecified",
    "Este relatório apresenta hipóteses com base nas linhas encontradas. Não confirma a causa sem validação adicional.": "This report presents hypotheses based on matching log lines. It does not confirm the cause without further validation.",
    "Metadados detetados": "Detected metadata",
    "Não foram detetados Title IDs, firmware ou versões reconhecíveis.": "No recognizable Title IDs, firmware, or version mentions were detected.",
    "Contexto fornecido": "Provided context",
    "Não foi fornecido contexto adicional.": "No additional context was provided.",
    "Resultados": "Findings",
    "Formato da origem": "Source format",
    "Armazenamento": "Storage",
    "Confiança": "Confidence",
    "Contexto": "Context",
    "Fontes": "Sources",
    "Não foi encontrada uma regra conhecida. Isso não significa que os logs estejam limpos; pode ser necessária uma regra nova ou contexto adicional.": "No known rule matched. This does not mean the logs are clean; a new rule or additional context may be needed.",
    "Gravidade indicativa": "Indicative severity",
    "Tipo de evidência": "Evidence type",
    "Compatibilidade com contexto": "Context match",
    "Evidência": "Evidence",
    "Possível correção / orientação": "Possible fix / guidance",
    "Aplicabilidade / limites": "Applicability / limitations",
    "Próximos passos sugeridos": "Suggested next steps",
    "Limites e privacidade": "Limitations and privacy",
    "A análise é local e baseada em assinaturas; a confiança refere-se à interpretação da mensagem, não à causa final.": "Analysis is local and signature-based; confidence refers to the interpretation of the message, not the final cause.",
    "Só foram incluídas linhas de evidência correspondentes; o log completo não é incluído automaticamente.": "Only matching evidence lines are included; the full log is not included automatically.",
    "Revê manualmente o relatório antes de o publicar, especialmente se desativaste a anonimização.": "Review the report manually before publishing it, especially if path/IP anonymization is disabled.",
    "A ferramenta não executa payloads, não altera configurações, não instala/desinstala títulos e não elimina ficheiros.": "The tool does not run payloads, change settings, install/uninstall titles, or delete files.",
    "A base inclui relatos de comunidade que podem estar por resolver; uma issue aberta ou workaround relatado não é uma correção universal.": "The database includes community reports that may remain unresolved; an open issue or reported workaround is not a universal fix.",
    "IDs dos títulos": "Title IDs",
    "Referências de firmware": "Firmware mentions",
    "Referências de versão": "Version mentions",
    "guia manual": "manual guide",
    "solução relatada — confirmar antes de aplicar": "reported fix — confirm before applying",
    "alternativa relatada pela comunidade": "community-reported workaround",
    "recolher mais dados; sem correção confirmada": "collect more data; no confirmed fix",
    "triagem manual": "manual triage",
    "triagem segura": "safe triage",
    "evitar temporariamente a operação": "temporarily avoid the operation",
    "não automatizar — requer validação manual": "do not automate — manual validation required",
    "pasta de jogo": "game folder",
    "imagem .ffpfs/.ffpfsc": "image .ffpfs/.ffpfsc",
    "imagem LZ4": "LZ4 image",
    "título já instalado": "installed title",
    "outro formato": "other format",
    "SSD interno": "internal SSD",
    "transferência entre USB e SSD interno": "USB-to-internal SSD transfer",
    "após retoma do modo de repouso": "after resuming from rest mode",
    "após sair/fechar o jogo": "after closing a game",
    "durante instalação/registo": "during installation/registration",
    "ao iniciar o jogo": "when launching a game",
    "durante cópia/movimentação de ficheiros": "during file copy/move",
    "em vários jogos": "multiple titles",
    "apenas num jogo": "one title only",
    "desconhecida": "unknown",
    "exemplo integrado (dados fictícios)": "built-in demo (sample data)",
    "Exemplo integrado": "Built-in demo",
    "exemplo fictício": "demo example",
    "logs da PS5": "PS5 logs",
    "logs carregados": "loaded logs",
})

# Knowledge-base translations are rebuilt when a verified remote database is installed.
# This lets new rules arrive with their own English text without requiring an app binary update.
_KB_TRANSLATIONS: dict[str, str] = {}


def register_knowledge_base(data: dict) -> None:
    global _TRANSLATIONS
    _KB_TRANSLATIONS.clear()
    for rule in data.get("rules", []):
        embedded = ((rule.get("translations") or {}).get("en") or {})
        translations = embedded if isinstance(embedded, dict) else {}
        if not translations:
            translations = RULE_EN.get(rule.get("id"), {})
        for field in ("title", "summary", "fix_summary", "applicability"):
            src = rule.get(field)
            dst = translations.get(field)
            if isinstance(src, str) and isinstance(dst, str):
                _KB_TRANSLATIONS[src] = dst
        src_steps = rule.get("steps", [])
        dst_steps = translations.get("steps", [])
        for src, dst in zip(src_steps, dst_steps):
            if isinstance(src, str) and isinstance(dst, str):
                _KB_TRANSLATIONS[src] = dst
    for entry in data.get("compatibility_matrix", []):
        translations = ((entry.get("translations") or {}).get("en") or {})
        if not isinstance(translations, dict):
            continue
        for field in ("title", "summary", "status"):
            src, dst = entry.get(field), translations.get(field)
            if isinstance(src, str) and isinstance(dst, str):
                _KB_TRANSLATIONS[src] = dst
    # Remove stale strings from an older database after an update/rollback.
    _TRANSLATIONS.clear()
    _TRANSLATIONS.update(UI_PT_EN)
    _TRANSLATIONS.update(_KB_TRANSLATIONS)


def set_language(language: str) -> None:
    global LANGUAGE
    LANGUAGE = "en" if str(language).lower().startswith("en") else "pt"


def tr(value, language: str | None = None):
    if not isinstance(value, str):
        return value
    lang = language or LANGUAGE
    if lang != "en":
        return value
    text = value
    for source in sorted(_TRANSLATIONS.keys(), key=len, reverse=True):
        target = _TRANSLATIONS[source]
        if source in text:
            text = text.replace(source, target)
    return text


def install_tkinter_translation() -> None:
    """Localize widget text as it is created; logs themselves are never translated."""
    global _PATCHED
    if _PATCHED:
        return
    OriginalLabel = ttk.Label
    OriginalButton = ttk.Button
    OriginalMenuButton = ttk.Menubutton
    OriginalCombo = ttk.Combobox
    OriginalNotebook = ttk.Notebook
    OriginalMenu = tk.Menu
    OriginalCheckbutton = tk.Checkbutton

    class LocalizedLabel(OriginalLabel):
        def __init__(self, master=None, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = tr(kwargs["text"])
            super().__init__(master, **kwargs)

    class LocalizedButton(OriginalButton):
        def __init__(self, master=None, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = tr(kwargs["text"])
            super().__init__(master, **kwargs)

    class LocalizedMenuButton(OriginalMenuButton):
        def __init__(self, master=None, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = tr(kwargs["text"])
            super().__init__(master, **kwargs)

    class LocalizedCombo(OriginalCombo):
        def __init__(self, master=None, **kwargs):
            if "values" in kwargs:
                kwargs["values"] = tuple(tr(item) for item in kwargs["values"])
            super().__init__(master, **kwargs)

    class LocalizedNotebook(OriginalNotebook):
        def add(self, child, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = tr(kwargs["text"])
            return super().add(child, **kwargs)

    class LocalizedCheckbutton(OriginalCheckbutton):
        def __init__(self, master=None, **kwargs):
            if "text" in kwargs:
                kwargs["text"] = tr(kwargs["text"])
            super().__init__(master, **kwargs)

    class LocalizedMenu(OriginalMenu):
        def add_command(self, *args, **kwargs):
            if "label" in kwargs:
                kwargs["label"] = tr(kwargs["label"])
            return super().add_command(*args, **kwargs)
        def add_checkbutton(self, *args, **kwargs):
            if "label" in kwargs:
                kwargs["label"] = tr(kwargs["label"])
            return super().add_checkbutton(*args, **kwargs)
        def add_cascade(self, *args, **kwargs):
            if "label" in kwargs:
                kwargs["label"] = tr(kwargs["label"])
            return super().add_cascade(*args, **kwargs)

    ttk.Label = LocalizedLabel
    ttk.Button = LocalizedButton
    ttk.Menubutton = LocalizedMenuButton
    ttk.Combobox = LocalizedCombo
    ttk.Notebook = LocalizedNotebook
    tk.Menu = LocalizedMenu
    tk.Checkbutton = LocalizedCheckbutton

    # Native message boxes and file picker titles use the same catalog.
    for name in ("showinfo", "showwarning", "showerror", "askyesno", "askokcancel", "askquestion"):
        original = getattr(messagebox, name)
        def make_messagebox(fn):
            def wrapped(*args, **kwargs):
                args = list(args)
                if len(args) > 0 and isinstance(args[0], str): args[0] = tr(args[0])
                if len(args) > 1 and isinstance(args[1], str): args[1] = tr(args[1])
                if "title" in kwargs: kwargs["title"] = tr(kwargs["title"])
                if "message" in kwargs: kwargs["message"] = tr(kwargs["message"])
                return fn(*args, **kwargs)
            return wrapped
        setattr(messagebox, name, make_messagebox(original))

    for name in ("askopenfilename", "askopenfilenames", "asksaveasfilename"):
        original = getattr(filedialog, name)
        def make_dialog(fn):
            def wrapped(*args, **kwargs):
                if "title" in kwargs: kwargs["title"] = tr(kwargs["title"])
                if "filetypes" in kwargs:
                    kwargs["filetypes"] = tuple((tr(label), pattern) for label, pattern in kwargs["filetypes"])
                return fn(*args, **kwargs)
            return wrapped
        setattr(filedialog, name, make_dialog(original))

    _PATCHED = True

_TRANSLATIONS.update(UI_PT_EN)
