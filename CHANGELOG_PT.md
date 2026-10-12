# Histórico de alterações

## v0.7.5 — Distribuição por GitHub Releases
- O workflow já não usa um `.spec` guardado no repositório; cria um spec temporário fora da raiz para evitar caminhos relativos obsoletos.
- Inclui a base de conhecimento a partir do caminho absoluto, corrigindo a referência errada a `build\knowledge_base.json`.
- Cada build disponibiliza um artifact do `.exe` e SHA-256 para testes.
- Ao publicar uma GitHub Release, o workflow anexa automaticamente o `.exe` e o checksum à Release.
- O utilizador final pode descarregar apenas `PS5HomebrewDoctor.exe`.

## v0.7.4 — Compilação cloud com diagnóstico melhorado
- Compilação direta a partir de `app.py`.
- Relatórios adicionais sobre a localização da saída.
