# PS5 Game Compatibility Atlas

**Um atlas comunitário, com fontes, dos resultados reportados na execução de jogos PS5 em configurações homebrew.** O site é bilingue (português de Portugal e inglês), responsivo e funciona sem servidor de aplicação.

> **Nota importante:** esta é a versão inicial de investigação, não uma lista definitiva. Os registos são observações públicas, podem ser contraditórios e não garantem que um jogo funcione noutra consola, firmware, versão ou formato. O projeto não aloja ficheiros. Os downloads na aplicação limitam-se a releases de homebrew e ficheiros com origem e hash publicados. Não agrega nem fornece cópias não autorizadas de jogos comerciais, dumps ou patches.

## Conteúdo da versão 0.2.0

- 83 registos de teste, relativos a 46 nomes de jogos/títulos.
- 18 fontes públicas indexadas: documentação do ShadowMountPlus, issues do GitHub e publicações/comentários comunitários.
- 7 guias de formato, distinguindo a indicação do mantenedor dos resultados observados.
- Pesquisa por jogo, Title ID, firmware, formato, sintomas e texto do relato.
- Filtros por firmware, formato, tipo de armazenamento e estado reportado.
- Resultados separados por configuração, incluindo relatos contraditórios.
- Ligação à publicação original, âmbito do teste, notas de cautela e qualidade da evidência.
- Novo separador **Downloads & sources** com o catálogo comunitário de homebrew `homebrew.page`, verificando a assinatura Ed25519 do manifesto e os SHA-256 do índice e das fichas, antes de confiar nesses metadados.
- Connectores para consultar as últimas releases do Orbit Store, Spectrum Library, PS5Library e repositórios GitHub personalizados.
- Fila local de downloads com progresso, pausa/retoma quando o host suporta HTTP Range, cancelamento e verificação SHA-256 antes de guardar ficheiros. A transferência só é oferecida quando o catálogo assinado também publica um hash para o artefacto.
- Fontes personalizadas guardadas apenas no navegador; sites como Vikingfile são abertos manualmente e não são analisados por scraper automático.
- Importação/exportação das fontes e da fila local.
- Contribuições guardadas localmente no navegador e exportação voluntária. Não existe backend e nada é enviado automaticamente.
- Exportação da base de relatos para CSV (inclui links de fonte) ou JSON.

## Executar localmente

O site é composto por ficheiros estáticos. Com Python instalado, abre um terminal na pasta do projeto e executa:

```bash
python -m http.server 8000
```

Depois abre `http://localhost:8000` no navegador. Também podes abrir `index.html` diretamente, mas um servidor local é preferível para persistência das contribuições no navegador.

## Publicar no GitHub Pages

1. Cria um repositório GitHub novo para **PS5 Game Compatibility Atlas**.
2. Carrega todos os ficheiros e pastas deste projeto para a raiz do ramo `main`.
3. Abre **Settings → Pages**.
4. Em **Build and deployment**, seleciona **Deploy from a branch**, escolhe `main` e `/ (root)`.
5. Guarda e espera que o GitHub Pages publique o site.

A interface de compatibilidade funciona sem servidor. O separador de downloads consulta serviços públicos (homebrew.page e GitHub API) apenas quando o utilizador abre o separador/consulta uma release. Não exige chaves de API. A disponibilidade do catálogo depende desses serviços e da política CORS do fornecedor.

## Atualizar os dados

Os dados de origem editáveis estão em `build_data.py`. Para gerar as duas cópias de dados usadas pela aplicação:

```bash
python build_data.py
```

Isto atualiza `data/atlas-data.json`, `data/atlas-data.js` e `data/atlas-reports.csv`. O segundo ficheiro permite que a versão estática funcione mesmo quando `index.html` é aberto em contextos `file://` com restrições de `fetch`.

Antes de publicar alterações, executa:

```bash
python -m unittest discover -s tests -v
node --check app.js
node --check downloads.js
node tests/downloads-smoke.cjs
```

Lê `METHODOLOGY.md`, `DOWNLOADS_SOURCES.md` e `CONTRIBUTING.md` antes de acrescentar resultados ou conectores. Não deduzas o firmware, formato, duração ou armazenamento que a fonte não indique. Para os campos em falta, utiliza uma indicação explícita de desconhecido.

## Estrutura

| Ficheiro | Finalidade |
|---|---|
| `index.html` | Página e estrutura da aplicação |
| `styles.css` | Interface responsiva e estilos |
| `app.js` | Pesquisa, filtros, idioma, contribuições locais e exportação |
| `downloads.js` | Catálogo homebrew, releases GitHub, fila e verificação SHA-256 |
| `data/atlas-data.json` | Dados curados em formato JSON |
| `data/atlas-reports.csv` | Registos de teste para abrir numa folha de cálculo, com ligações às fontes |
| `data/atlas-data.js` | Cópia dos dados para carregamento estático/offline |
| `build_data.py` | Fonte editável dos registos e guias de formato |
| `METHODOLOGY.md` | Âmbito, classificação da evidência e limitações |
| `DOWNLOADS_SOURCES.md` | Conectores, limites da fila e orientações para fontes autorizadas |
| `RESEARCH_NOTES.md` | Síntese dos principais padrões e resultados contraditórios encontrados |
| `CONTRIBUTING.md` | Regras para inserir e rever resultados |
| `tests/test_dataset.py` | Verificações de integridade do dataset |

## Licenças

O código do projeto está sob a licença MIT, em `LICENSE.txt`. Os resumos e metadados editoriais do Atlas são disponibilizados sob CC BY 4.0, com atribuição às fontes públicas originais, conforme `DATA-LICENSE.md`. As fontes e marcas citadas pertencem aos respetivos titulares.

O Atlas é um projeto comunitário independente, sem afiliação ou endosso da Sony Interactive Entertainment, PlayStation ou dos autores das ferramentas referidas.
