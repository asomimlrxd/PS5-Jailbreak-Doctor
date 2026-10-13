# Metodologia de investigação

**Corte inicial da investigação:** 13 de outubro de 2026.  
**Versão da base de compatibilidade:** 0.1.0.
**Versão da aplicação:** 0.2.0 (inclui downloads de homebrew).  
**Base inicial:** 83 registos, 46 nomes de jogos/títulos, 18 fontes e 7 guias de formato.

## Âmbito

O Atlas regista observações públicas sobre jogos e ferramentas em ambientes PS5 homebrew. Dá prioridade a relatos que indiquem pelo menos parte da configuração: firmware, formato, armazenamento, versões das ferramentas e o que aconteceu durante o teste.

A pesquisa inicial cruza:

- documentação pública do ShadowMountPlus;
- issues do repositório do ShadowMountPlus;
- threads e comentários públicos do Reddit, incluindo uma megathread do firmware 13.60, uma lista focada no SSD original e um tópico de testes APR no SSD M.2 de expansão;
- uma folha comunitária referenciada numa das threads;
- uma lista histórica de firmware, mantida apenas como referência e não misturada com testes de runtime.

## Como os registos são criados

Os resumos são paráfrases compactas da publicação original. Cada registo aponta para a fonte que o sustenta. Não copiamos comentários extensos nem assumimos informação que não foi indicada. Quando uma thread tem firmware de contexto, mas o comentário individual não repete o valor, o registo identifica-o explicitamente como contexto da thread.

A folha comunitária de Google Sheets foi localizada, mas a vista pública acessível durante a pesquisa não mostrou a grelha completa dos resultados. Por isso, o Atlas não importa valores dessa grelha que não tenha conseguido verificar. A ligação continua disponível na secção de fontes para que possa ser consultada manualmente.

## Estados reportados

- **Concluído sem problemas reportados:** o autor diz ter concluído o jogo ou descreve funcionamento sem problemas num âmbito declarado. Não significa compatibilidade universal.
- **Jogável com problemas:** inicia ou é jogável, mas há stutter, áudio, texturas, freezes ou outros defeitos.
- **Teste curto / preliminar:** o jogo foi iniciado ou testado durante pouco tempo, sem prova de estabilidade prolongada ou conclusão.
- **Problema resolvido no relato:** o autor relata que uma alteração resolveu aquele caso específico.
- **Não inicia / ecrã preto:** o autor não consegue iniciar o jogo naquele cenário.
- **Crash / freeze:** há um crash ou bloqueio reportado durante o teste.

Os estados descrevem o relato original, não um ensaio controlado do Atlas. Se existirem configurações contraditórias, cada uma tem o seu próprio registo.

## Qualidade da evidência

- **Alta:** documentação ou issue detalhada com contexto e comportamento reprodutível declarado.
- **Média:** formato, firmware ou versões e resultado descritos com algum detalhe.
- **Baixa:** comentário curto, configuração incompleta, firmware herdado do contexto da thread ou resultado preliminar.

Estes níveis não são scores científicos nem percentagens de probabilidade. Um relato bem documentado ainda pode estar errado ou aplicar-se apenas à configuração descrita.

## Como ler os formatos

A secção «Formatos» separa documentação do mantenedor e relatos dos utilizadores. Na documentação consultada, `.ffpkg`/UFS é a opção recomendada para uso geral, `.exfat` destina-se a compatibilidade com títulos específicos e PFS (`.ffpfs`/`.ffpfsc`) está marcado como experimental. «Folder / dump» e etiquetas comunitárias como LZ4 são mantidas como a fonte as descreve; não são comparadas como se fossem formatos equivalentes em testes controlados.

Também é essencial distinguir o SSD interno original da consola, o SSD M.2 de expansão e unidades USB/externas. O termo «interno» em algumas publicações é ambíguo; o Atlas conserva uma nota quando a thread especifica o slot de expansão.

## Separação entre compatibilidade e downloads

O separador de compatibilidade continua a ser baseado em relatos sobre jogos e configurações. O separador de downloads é separado e consulta o catálogo comunitário `homebrew.page` para aplicações homebrew nativas. Antes de confiar no índice e nas fichas, o Atlas verifica a assinatura Ed25519 do `manifest.json` através das chaves públicas documentadas pelo catálogo e compara o SHA-256 exato dos ficheiros JSON com o manifesto assinado. O artefacto descarregado é depois comparado com o SHA-256 publicado na ficha assinada. Isto melhora a autenticidade dos metadados e a integridade do ficheiro, mas não equivale a uma auditoria independente de segurança nem prova, por si só, os direitos de distribuição.

Orbit Store, Spectrum Library e PS5Library são apresentados como projetos externos e as suas páginas/releases oficiais podem ser consultadas. O Atlas não importa os catálogos de jogos dessas aplicações. Vikingfile é apenas um link manual para a página do fornecedor: não há scraper automático, resolução de links temporários, bypass de CAPTCHA nem integração para descarregar conteúdo de catálogos de jogos. As fontes personalizadas são locais e requerem confirmação do utilizador de que tem autorização para aceder/utilizar os ficheiros.

Downloads diretos só são colocados na fila quando a origem é um catálogo de homebrew ou uma release GitHub e existe um SHA-256 publicado. O navegador precisa de CORS para ler o ficheiro, suporta transferência direta até 120 MB e só permite guardar o blob depois de confirmar o hash. Se o servidor não suportar Range, a retoma começa novamente do início; se CORS bloquear a leitura, a aplicação apresenta a página oficial em vez de contornar a proteção.

## Exclusões e limitações

- Não alojamos jogos, dumps, patches nem ligações de descarga.
- Uma lista histórica de firmware mínimo/requisito do jogo não prova que esse jogo funcione num ambiente homebrew; não é fundida com os resultados de runtime.
- Não atribuímos a um comentário o firmware, hardware, formato ou ferramentas do autor original da thread sem evidência.
- Não apresentamos uma mudança de configuração relatada como solução garantida ou recomendação universal.
- Os números de registos não medem a popularidade nem a probabilidade de sucesso de um jogo.
- A internet muda continuamente. Esta base é um primeiro corte manual, não uma cobertura exaustiva de todas as comunidades, idiomas, posts, patches ou versões de jogos.
- A pesquisa pode não encontrar threads privadas, removidas, bloqueadas ou indexadas de forma incompleta. A folha comunitária referenciada ainda requer verificação humana da sua grelha completa.

## Melhorias para futuras revisões

1. Importação/revisão da folha comunitária quando os dados puderem ser verificados por célula.
2. Recolha estruturada de mais fontes GitHub/Reddit e, sempre que possível, fóruns de diferentes idiomas.
3. Campos adicionais para data exata do teste, versão dos payloads, versão do jogo, tipo de consola, duração e conclusão.
4. Detetar duplicados por Title ID e configuração sem eliminar relatos com resultados divergentes.
5. Fluxo de contribuição moderado antes da inclusão na base pública.
