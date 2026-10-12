# Histórico de versões

## v0.7.4 — Compilação cloud com diagnóstico melhorado
- O workflow compila diretamente `app.py` com as opções one-file do PyInstaller, sem usar o `PS5HomebrewDoctor.spec` existente no repositório.
- O spec temporário é criado fora do checkout para evitar conflito com specs antigos e caminhos de recursos desatualizados.
- São validados os ficheiros de origem e a base JSON antes da compilação.
- Se o EXE não aparecer no caminho esperado, o workflow lista o conteúdo de `dist`, procura saídas alternativas e apresenta ficheiros de build úteis para depuração.
- O artifact continua a ser um único `PS5HomebrewDoctor.exe`.

## v0.7.3 — Correção robusta do caminho da base de conhecimento
- Adicionado um spec na raiz e validação de caminhos.

## v0.7.2 — Correção da compilação na cloud
- Ajuste ao caminho da base de conhecimento passado ao PyInstaller.

## v0.7.1 — Edição One File
- O executável incorpora os componentes da aplicação.

## v0.7.0
- Seletor de idioma PT/EN e preferências guardadas.
