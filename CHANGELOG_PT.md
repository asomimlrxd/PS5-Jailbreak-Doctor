## v0.7.3 — Correção robusta do caminho da base de conhecimento
- Adicionado um ficheiro `PS5HomebrewDoctor.spec` na raiz do projeto. O spec procura `app.py` e `knowledge_base.json` na sua própria pasta ou na pasta imediatamente acima, por isso não depende de `build\knowledge_base.json`.
- O workflow limpa saídas antigas, valida os ficheiros de origem e compila explicitamente a partir do spec corrigido.
- O artifact continua a ser um único `PS5HomebrewDoctor.exe`; os utilizadores finais não precisam de Python, PyInstaller ou ficheiros BAT.
- A documentação agora pede substituir o workflow e o spec antigos, e confirma que `knowledge_base.json` tem de permanecer na raiz do repositório.

# Histórico de versões

## v0.7.2 — Correção da compilação na cloud
- Corrigido o caminho de `knowledge_base.json` passado ao PyInstaller: agora é resolvido como caminho absoluto a partir da raiz do repositório, em vez de ser interpretado relativamente à pasta `build`.
- O workflow verifica explicitamente se o ficheiro da base de conhecimento existe antes de iniciar a compilação.
- Mantida a saída como um único `PS5HomebrewDoctor.exe`, sem Python ou BAT necessários no computador de destino.

## v0.7.1 — Edição One File
- Simplificado o pacote para conter apenas um BAT de compilação, código necessário, base de conhecimento e documentação essencial.
- O script cria `PS5HomebrewDoctor.exe` diretamente na pasta do projeto, sem criar pastas `build` e `dist` dentro dela.
- O executável incorpora a base de conhecimento e utiliza o modo `onefile` e `windowed` do PyInstaller.
- Atualizada a versão exibida e nos relatórios para 0.7.1.

## v0.7.0
- Seletor de idioma PT/EN e preferências de idioma guardadas.
- Ferramenta de compilação one-file inicial.
