# PS5 Jailbreak Doctor

**O PS5 Jailbreak Doctor é uma aplicação de diagnóstico para Windows destinada à comunidade de homebrew da PS5.** Analisa logs, procura padrões de erro conhecidos associados a ferramentas como ShadowMountPlus e KStuff Lite, apresenta a evidência encontrada e sugere verificações seguintes.

> **Importante:** é um assistente de diagnóstico, não um jailbreak nem um exploit. Não instala payloads, não altera o firmware, não instala jogos e não aplica correções automaticamente na consola.

[README principal do GitHub](README.md) · [English](README_EN.md)

![Resultados de diagnóstico com dados de exemplo](./docs/images/diagnostic-results.png)

*Captura ilustrativa da vista de resultados com dados de exemplo — não significa que estes erros estejam presentes em todas as consolas.*

## O que faz

- **Analisa ficheiros de logs:** permite importar ficheiros `.log`, `.txt` e `.json` para análise local.
- **Obtém logs da PS5:** opcionalmente, liga-se à API HTTP do ShadowMountPlus na rede local para consultar a versão e obter o `debug.log` e o kernel log.
- **Deteta padrões conhecidos:** compara as linhas encontradas com uma base de conhecimento local em `knowledge_base.json`, que pode ser ampliada por contribuidores.
- **Usa contexto adicional:** firmware, versões do ShadowMountPlus e KStuff Lite, localização do jogo (USB/SSD interno), formato (pasta/imagem) e o momento em que o erro começou podem ajudar a avaliar a relevância de uma regra.
- **Explica cada resultado:** mostra evidências, confiança estimada, estado da fonte, limitações e passos sugeridos.
- **Evidência em primeiro lugar:** os resultados mostram as linhas correspondentes, o nível de confiança estimado, as limitações e os passos seguintes.
- **Notas de compatibilidade contextual:** combinações exatas de firmware, versões de ShadowMountPlus/KStuff Lite, formato da origem e momento do erro podem gerar avisos separados dos diagnósticos encontrados nos logs. Uma nota não prova que o erro aconteceu.
- **Verificação do scanner, só de leitura:** consulta as raízes personalizadas e as origens de `manual.lst` através dos endpoints suportados da API. Não inicia uma nova varredura nem altera configurações; versões antigas podem não disponibilizar estes dados.
- **Cronologia de erros:** destaca as primeiras linhas suspeitas pela ordem do ficheiro, preservando o texto original.
- **Atualizações verificadas da base de diagnósticos:** procura manualmente uma base mais recente, valida o SHA-256 e o esquema JSON, guarda uma cópia anterior e permite reverter. Só transfere regras; nunca envia logs.
- **Relatórios para a comunidade:** incluem a versão da base e um modelo opcional para indicar se os passos foram testados e se resolveram o problema.
- **Sinaliza erros ainda desconhecidos:** se encontra termos associados a erros/crashes sem regra correspondente, pode mostrá-los para análise posterior.
- **Exporta relatórios:** permite guardar um relatório para partilhar com a comunidade. A opção de anonimização oculta endereços IP e formatos comuns de caminhos de utilizador.
- **Respeita o idioma escolhido:** os relatórios são gerados em português ou inglês conforme o idioma da interface; a evidência original dos logs é mantida sem alterações.
- **Inclui português e inglês**, bem como temas claro e escuro com preferência guardada localmente.
- **Oferece algumas renomeações locais reversíveis:** apenas para cenários de nomes de ficheiros `.ffpfs`/`.ffpfsc previstos pela aplicação. A ação muda o nome do ficheiro no PC; não altera o seu conteúdo nem escreve diretamente na PS5.

## Como funciona

![Fluxo de diagnóstico](./docs/images/data-flow.png)

A análise de logs importados funciona localmente e não exige ligação à consola. Para obter logs automaticamente, o PC e a PS5 têm de estar na mesma rede local de confiança e a API do ShadowMountPlus tem de aceitar ligações pela rede.

![Painel de ligação ao ShadowMountPlus](./docs/images/connection-panel.png)

*A captura original foi editada para substituir o endereço IP privado por um marcador.*

## Utilização rápida

### Analisar logs que já tens no PC

1. Abre o programa.
2. Escolhe **Importar logs** e seleciona um ou mais ficheiros suportados.
3. Clica em **Analisar logs**.
4. Abre cada resultado para ver as linhas encontradas, as limitações e os próximos passos.
5. Guarda um relatório para o partilhares num tópico ou com os mantenedores da ferramenta relevante.

### Obter logs diretamente da PS5 (modo recomendado)

1. Confirma que o ShadowMountPlus está a funcionar e que a API está ativa. A configuração predefinida do ShadowMountPlus 1.7 tem `api_enabled=1` e `api_bind_address=127.0.0.1`.
2. No separador **Ligação à PS5**, deixa selecionado **Relay ELF (sem alterar config.ini)**. Se ainda não existir um IP guardado, introduz o IP LAN atual da PS5; fica guardado nas preferências locais do Doctor.
3. Confirma que o loader de payloads compatível está ativo na consola (normalmente recebe payloads na porta TCP `9021`) e clica em **Ligação automática (sem config.ini)**.
4. O Doctor procura primeiro um relay ativo. Se não encontrar nenhum, envia o ELF incluído para o endereço da PS5 e espera que o relay inicie. A ligação usa a porta TCP `10102` e a descoberta automática usa UDP `10103`.
5. Quando aparecer **Ligação confirmada**, clica em **Obter logs e analisar**.

O relay lê `/data/shadowmount/config.ini`, mas nunca o altera. Se o ShadowMountPlus estiver configurado para escutar apenas no IP LAN específico da consola, o relay também tenta disponibilizar localmente `127.0.0.1:10101` para que o launcher integrado continue a funcionar. Depois de um reinício completo da PS5, o relay tem de ser carregado novamente, a menos que uses um autoloader de payloads.

Se a descoberta por broadcast for bloqueada pela rede/firewall, a aplicação tenta ligar diretamente ao IP guardado. Se o loader da porta `9021` não estiver ativo, carrega `PS5JailbreakDoctorRelay.elf` através do loader existente e volta a clicar em **Procurar relay na rede**. Se a API estiver explicitamente desativada (`api_enabled=0`), o relay não a ativa nem edita a configuração; será necessário ativá-la através de uma opção oficial disponível na versão instalada ou reconfigurá-la manualmente.

### Modo de API direta (alternativa)

O modo **API direta** destina-se a versões/configurações do ShadowMountPlus que já permitem ligações a partir da rede local. A API HTTP padrão escuta apenas em `127.0.0.1:10101`; nesse estado, o PC não consegue aceder diretamente. Em versões com o controlo LAN na interface do ShadowMountPlus, usa essa opção em vez de editar ficheiros. A configuração manual `api_bind_address=0.0.0.0` continua a ser uma alternativa, mas não é necessária no modo Relay ELF.

### Segurança da ligação

A API do ShadowMountPlus e o relay não usam autenticação de utilizador. O relay aceita clientes de endereços IPv4 privados e expõe apenas endpoints de leitura de versão, logs e configuração do scanner; ainda assim, os logs podem conter identificadores. Usa apenas uma rede privada de confiança e nunca encaminhes as portas TCP `10102` ou UDP `10103` no router, nem exponhas a API à Internet.

## Como interpretar os resultados

- Um padrão reconhecido é **uma pista**, não uma prova definitiva da causa.
- A confiança é uma estimativa baseada na regra e na evidência disponível, não uma garantia estatística.
- Um resultado com baixa confiança ou não classificado precisa de contexto: log completo, firmware, versões e a ação exata que causou o problema.
- As sugestões são apresentadas para avaliação pelo utilizador. O programa não altera a PS5 através da API.


## Atualizar a base de diagnósticos

Em **Mais opções → Atualizar base de diagnósticos**, a aplicação procura uma versão mais recente. Depois de confirmares, transfere apenas `knowledge_base.json` deste repositório, valida o SHA-256 indicado em `updates.json`, verifica o esquema e as traduções inglesas e guarda a nova base na pasta de dados do utilizador. A versão anterior fica guardada localmente e pode ser restaurada em **Mais opções → Reverter atualização da base**. O executável não é atualizado automaticamente e nenhum log, relatório ou endereço da consola é enviado.

O ficheiro `updates.json` tem de ser publicado em conjunto com a versão correspondente de `knowledge_base.json` no ramo principal. Se estes ficheiros ainda não estiverem publicados, a atualização não estará disponível através da aplicação.

## Privacidade e segurança

- Por defeito, os logs são analisados localmente; não são enviados automaticamente para um servidor do projeto.
- A ligação à consola só acontece quando carregas num botão de ligação ou recolha.
- A anonimização do relatório substitui endereços IP e caminhos comuns de pastas de utilizador. Antes de partilhar, revê o relatório: caminhos personalizados, nomes de utilizador noutros formatos, Title IDs e outros identificadores podem permanecer.
- A API do ShadowMountPlus não tem autenticação; usa-a apenas numa rede privada de confiança.
- Antes de executar uma renomeação local, confirma o ficheiro selecionado e guarda cópia de segurança se for importante. A aplicação bloqueia a reversão quando existe um conflito de nome ou o ficheiro foi modificado após a ação.

## Instalar e executar

### Executável Windows

Na página **Releases** do repositório, descarrega `PS5HomebrewDoctor.exe` da versão mais recente. O executável compilado não exige Python nem ficheiros `.bat` no computador do utilizador.

O workflow do GitHub Actions compila o programa para Windows x64 e, quando é publicada uma Release, anexa o executável e o respetivo ficheiro SHA-256. O executável não tem assinatura comercial; o Windows SmartScreen pode mostrar um aviso.

### Executar a partir do código-fonte

Requer Python 3.10 ou posterior. A interface e a análise usam a biblioteca padrão do Python.

```powershell
py -3.12 app.py
```

### Compilar o EXE no Windows

Para a compilação documentada, utiliza Python 3.12 e instala o PyInstaller:

Para incluir a ligação automática, compila primeiro `ps5-relay/relay.c` com o [PS5 Payload SDK oficial](https://github.com/ps5-payload-dev/sdk) e coloca o resultado em `ps5-relay/build/PS5JailbreakDoctorRelay.elf`. Depois usa:

```powershell
py -3.12 -m pip install --upgrade pyinstaller
py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed --name PS5HomebrewDoctor --add-data "knowledge_base.json;." --add-data "ps5-relay/build/PS5JailbreakDoctorRelay.elf;payloads" app.py
```

O ficheiro resultante é criado em `dist\PS5HomebrewDoctor.exe`. O workflow incluído em `.github/workflows/build-windows-exe.yml` é recomendado para publicações oficiais: compila o relay ELF com uma versão fixada do SDK, valida os ficheiros, inclui a base de conhecimento, executa os testes de regressão e anexa checksums SHA-256.

## Estrutura do projeto

| Ficheiro | Função |
|---|---|
| `app.py` | Interface Windows e integração com a API do ShadowMountPlus |
| `doctor_core.py` | Motor de diagnóstico, evidências e relatórios |
| `knowledge_base.json` | Base local de padrões de erro, com fontes e recomendações |
| `safe_actions.py` | Conjunto limitado de renomeações locais reversíveis |
| `i18n.py` | Textos da interface em português e inglês |
| `updates.py` / `updates.json` | Atualizações explícitas da base com verificação SHA-256 |
| `relay_client.py` | Descoberta do relay e carregamento através de um loader de payloads compatível |
| `ps5-relay/relay.c` | Relay LAN só de leitura e alias local para o ShadowMountPlus |
| `UPDATES.md` | Guia para publicar atualizações da base de diagnósticos |
| `tests/` | Testes de regressão para traduções, diagnósticos e atualizações |
| `CHANGELOG.md` | Alterações do projeto organizadas por versão |
| `.github/workflows/build-windows-exe.yml` | Compila o relay ELF e o EXE para Windows x64 |
| `FONTES_PT.md` | Referências públicas usadas nas regras da base de conhecimento |

## Limitações conhecidas

A base de conhecimento não cobre todos os erros possíveis e os relatos comunitários podem ser específicos de uma versão ou firmware. A aplicação não consegue garantir que uma sugestão resolva o problema. Confirma sempre as fontes originais e verifica a compatibilidade antes de alterar ficheiros ou configurações.

## Licença e aviso legal

O projeto é distribuído ao abrigo da licença MIT; consulta [`LICENSE.txt`](LICENSE.txt).

Este é um projeto comunitário experimental. Não é afiliado, patrocinado ou apoiado pela Sony Interactive Entertainment, PlayStation, etaHEN, ShadowMountPlus ou pelos responsáveis do KStuff Lite. As marcas pertencem aos respetivos proprietários. Utiliza o programa por tua conta e risco.
