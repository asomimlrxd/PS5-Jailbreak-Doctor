# PS5 Homebrew Doctor v0.7.4 — gerar um EXE autónomo no GitHub Actions

O objetivo é obter um único `PS5HomebrewDoctor.exe`. O PC onde vais usar a aplicação não precisa de Python nem de ficheiros BAT. A compilação ocorre num runner Windows temporário do GitHub Actions.

## O que esta versão corrige

O erro `O executável não foi criado` é a verificação final a dizer que o `.exe` não apareceu no caminho esperado; por si só, não mostra a causa original. Esta versão compila diretamente `app.py`, cria o spec temporário fora do repositório, valida os ficheiros antes da compilação e imprime mais informação caso não encontre a saída.

**Importante:** como a mensagem do erro anterior está em português e o workflow v0.7.3 distribuído usava outra mensagem, confirma que o GitHub executa o workflow atualizado e não uma cópia antiga ou um segundo workflow.

## Preparar o repositório

1. Descarrega e extrai este ZIP localmente.
2. No repositório GitHub do projeto, substitui os ficheiros fonte pelos desta versão.
3. Substitui especificamente `.github/workflows/build-windows-exe.yml` pelo ficheiro desta versão.
4. Abre `.github/workflows/` no GitHub e confirma que não há outro workflow antigo a tentar criar o mesmo EXE. Remove os workflows duplicados/antigos que executem a compilação anterior. O ficheiro `PS5HomebrewDoctor.spec` antigo pode ser removido; o workflow novo não o utiliza.
5. Confirma que `app.py`, `doctor_core.py`, `app_paths.py`, `i18n.py`, `safe_actions.py`, `session_utils.py` e `knowledge_base.json` estão na raiz do repositório.
6. Faz commit das alterações.

## Compilar e descarregar

1. Abre o separador **Actions** no GitHub.
2. Seleciona **Build PS5 Homebrew Doctor EXE** e abre a execução mais recente, iniciada pelo teu último commit. Não uses uma execução antiga.
3. Espera pelo visto verde.
4. Na secção **Artifacts**, descarrega `PS5HomebrewDoctor-Windows-x64`.
5. Extrai o ZIP do artifact. O resultado é `PS5HomebrewDoctor.exe`; copia-o para uma pasta e abre com duplo clique.

## Se voltar a falhar

Abre a execução que ficou a vermelho e copia o log completo do passo **Build one-file EXE directly from app.py**, incluindo as linhas anteriores à mensagem de erro. A versão 0.7.4 imprime o comando, versão do PyInstaller, conteúdo da pasta `dist` e ficheiros recentes de build. Esses dados são necessários para distinguir uma falha real do compilador de uma saída colocada noutra pasta.

## Privacidade e segurança

- A app analisa logs localmente; o workflow compila o código fonte do repositório e publica o executável como artifact.
- O EXE não é assinado por um certificado comercial; o SmartScreen pode mostrar um aviso.
- Mantém a API de leitura do ShadowMountPlus apenas numa rede local de confiança. Não a exponhas à Internet.

## Fontes

- Documentação do PyInstaller sobre opções de compilação: https://pyinstaller.org/en/stable/usage.html
- Documentação do PyInstaller sobre ficheiros spec: https://pyinstaller.org/en/stable/spec-files.html
- Documentação do GitHub Actions sobre artifacts: https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts
