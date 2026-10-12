# PS5 Homebrew Doctor v0.7.2 — criar EXE sem Python instalado no teu PC

Este pacote usa o GitHub Actions para compilar a aplicação num computador Windows temporário na cloud. **Não precisas de instalar Python nem PyInstaller no teu computador.** O resultado para uso diário é um único ficheiro `PS5HomebrewDoctor.exe`.

## O que vais precisar

- Uma conta GitHub (gratuita).
- Ligação à Internet para enviar o código e descarregar o EXE.
- Não precisas de ter Python instalado localmente.

## Passos

1. Extrai o ZIP para uma pasta. Deves ver `app.py`, `doctor_core.py`, `knowledge_base.json` e a pasta `.github`.
2. Abre <https://github.com/new> e cria um repositório, por exemplo `PS5-Homebrew-Doctor`. Podes escolher **Private** para manter o código privado.
3. Dentro da pasta do repositório no GitHub, escolhe **Add file → Upload files**. Arrasta para a página o conteúdo extraído desta pasta, incluindo a pasta `.github` (que contém `workflows/build-windows-exe.yml`). Não carregues o ZIP em si; carrega os ficheiros extraídos.
4. Confirma que `app.py`, `knowledge_base.json` e `.github/workflows/build-windows-exe.yml` aparecem no carregamento. Clica em **Commit changes**.
5. Abre o separador **Actions** no repositório. A execução **Build PS5 Homebrew Doctor EXE** deverá iniciar automaticamente após o commit. Abre a execução e espera que termine com um visto verde.
6. Na página dessa execução, procura a secção **Artifacts** e descarrega `PS5HomebrewDoctor-Windows-x64`.
7. Extrai o ZIP do artifact. Lá dentro estará `PS5HomebrewDoctor.exe`.
8. Copia esse EXE para uma pasta normal no Windows e abre-o com duplo clique. Para uso diário, não precisas dos ficheiros-fonte, de Python nem de ficheiros `.bat`.

A documentação oficial do GitHub confirma que os ficheiros podem ser enviados por **Add file → Upload files** e que os artifacts de uma execução se descarregam a partir de **Actions → execução → Artifacts**.

## Se o workflow não iniciar

- Confirma que o ficheiro `.github/workflows/build-windows-exe.yml` foi enviado e está no caminho exato indicado.
- Abre **Actions** e confirma se a execução está à espera de aprovação ou se está desativada.
- Se não aparecer uma execução, abre **Actions → Build PS5 Homebrew Doctor EXE → Run workflow** (quando essa opção estiver disponível).
- Se a compilação falhar, abre a execução e envia-me o texto do passo que ficou a vermelho. A versão 0.7.2 usa o caminho absoluto de `knowledge_base.json`, evitando o erro em que o PyInstaller procurava o ficheiro dentro de `build`.

## Notas de segurança e privacidade

- O workflow compila o código incluído neste pacote e publica apenas o EXE como artifact; não publica secrets.
- Se o repositório for privado, só utilizadores com acesso ao repositório poderão ver e descarregar o artifact.
- O executável não vem assinado com um certificado de editor, por isso o Windows SmartScreen pode mostrar um aviso. Isso não é por si só prova de malware; confirma que o EXE foi descarregado da tua própria execução de compilação.
- A ligação à PS5 usa a API de leitura do ShadowMountPlus. Mantém essa API apenas na rede local de confiança; não a exponhas à Internet.

## O que é incorporado

O build usa PyInstaller em modo `--onefile --windowed` e inclui `knowledge_base.json`. O Python e as bibliotecas necessárias ficam dentro do EXE; o Python é usado apenas pelo computador de compilação temporário do GitHub Actions.
