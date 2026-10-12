# PS5 Homebrew Doctor v0.7.5 — EXE pronto para distribuir

Esta versão prepara o projeto para publicar um único executável Windows (`PS5HomebrewDoctor.exe`) nas **GitHub Releases**. Quem descarrega o programa não precisa de instalar Python, usar ficheiros `.bat` nem obter os ficheiros-fonte.

## Porque falhava a compilação anterior?

O erro `Unable to find ... build\knowledge_base.json` vem de um ficheiro `.spec` antigo que guardava o caminho da base de conhecimento relativamente à pasta de build. O workflow desta versão **não utiliza `PS5HomebrewDoctor.spec`**: gera um spec temporário fora do repositório e passa o caminho absoluto para `knowledge_base.json`. Assim evita herdar os caminhos antigos.

## Atualizar o repositório

1. Descarrega e extrai este ZIP.
2. Copia os ficheiros desta pasta para a raiz do teu repositório GitHub, incluindo a pasta `.github`.
3. Substitui o workflow anterior por `.github/workflows/build-windows-exe.yml`. Remove workflows antigos que ainda chamem `PS5HomebrewDoctor.spec` ou usem `build\knowledge_base.json`.
4. Confirma que `app.py`, `app_paths.py`, `doctor_core.py`, `i18n.py`, `safe_actions.py`, `session_utils.py` e `knowledge_base.json` ficam na raiz do repositório.
5. Faz commit e push para `main` ou `master`.

## Testar uma compilação

1. No GitHub, abre **Actions** e seleciona **Build and publish PS5 Homebrew Doctor**.
2. Abre a execução mais recente e aguarda que termine com sucesso.
3. Em **Artifacts**, descarrega `PS5HomebrewDoctor-Windows-x64` e extrai-o. O ZIP contém o `.exe` e o seu SHA-256.

O artifact de Actions é temporário (30 dias). Para uma ligação de download estável e pública, usa o processo de Release abaixo.

## Publicar o EXE para toda a comunidade

1. No GitHub, abre **Releases** → **Draft a new release**.
2. Cria uma nova tag, por exemplo `v0.7.5`, apontando para o commit que queres distribuir.
3. Escreve um título como `PS5 Homebrew Doctor v0.7.5` e publica a Release.
4. O workflow compila o programa num runner Windows e anexa automaticamente `PS5HomebrewDoctor.exe` e `PS5HomebrewDoctor.exe.sha256` a essa Release.
5. Na página da Release, a comunidade descarrega apenas `PS5HomebrewDoctor.exe`. Não precisa de Python, `.bat` nem ficheiros-fonte.

## Notas importantes

- A compilação Windows ocorre em GitHub Actions; o PC do utilizador final não compila nada.
- O executável não tem assinatura comercial, por isso o Windows SmartScreen pode mostrar um aviso.
- Mantém a API do ShadowMountPlus limitada a uma rede local de confiança; não a exponhas à Internet.
- Os dados mutáveis (configuração e histórico) são guardados na pasta de utilizador da aplicação, não dentro do executável temporário.

## Documentação oficial

- PyInstaller — inclusão de ficheiros de dados: https://pyinstaller.org/en/stable/spec-files.html
- GitHub Actions — guardar e descarregar artifacts: https://docs.github.com/en/actions/tutorials/store-and-share-data
- GitHub Actions — permissões e workflows: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
