# Corrigir erro `build\\knowledge_base.json` no GitHub Actions

O erro indica que uma execução ainda está a utilizar um ficheiro `PS5HomebrewDoctor.spec` antigo que referencia `knowledge_base.json` relativamente à pasta `build`. O workflow incluído aqui não utiliza o `.spec` do repositório: cria o spec temporário fora do projeto e passa o caminho absoluto da base de dados.

## Aplicar a correção

1. No repositório GitHub, abre `Code` e entra em `.github/workflows/`.
2. Substitui o conteúdo de `build-windows-exe.yml` pelo ficheiro incluído neste pacote.
3. Procura outros ficheiros `.yml`/`.yaml` nessa pasta. Se algum workflow antigo também compilar a aplicação usando `PS5HomebrewDoctor.spec`, remove-o ou desativa-o. O GitHub executa todos os workflows aplicáveis; atualizar apenas um não impede outro antigo de falhar.
4. Confirma que estes ficheiros estão na raiz do repositório: `app.py`, `app_paths.py`, `doctor_core.py`, `i18n.py`, `safe_actions.py`, `session_utils.py` e `knowledge_base.json`.
5. Não é necessário usar `PS5HomebrewDoctor.spec` com este workflow. Podes removê-lo do repositório se nenhum outro processo precisar dele.
6. Faz commit das alterações e abre `Actions` para executar a workflow atualizada. Não basta voltar a executar uma execução falhada de um commit antigo.

## O que a versão corrigida faz

- valida os ficheiros de origem e a base de dados antes de compilar;
- usa o caminho absoluto para `knowledge_base.json`;
- gera o spec do PyInstaller numa pasta temporária fora do repositório;
- compila um único `PS5HomebrewDoctor.exe` e valida que foi criado;
- publica o executável e o checksum SHA-256 como artefactos da execução.
