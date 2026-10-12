# Atualizações da base de diagnósticos

A aplicação não atualiza automaticamente o executável. O botão **Atualizar base de diagnósticos** consulta `updates.json` e, apenas após confirmação explícita, transfere a base de regras indicada.

## Publicar uma nova base

1. Atualiza `knowledge_base.json` e aumenta `database_version`.
2. Cada regra nova ou modificada deve incluir `translations.en` para `title`, `summary`, `fix_summary`, `applicability` (quando existirem) e o mesmo número de passos traduzidos que `steps`. As notas da `compatibility_matrix` também devem incluir `translations.en` para `title`, `summary` e `status`.
3. Calcula o SHA-256 dos bytes exatos do ficheiro final `knowledge_base.json`.
4. Atualiza `updates.json` com a nova versão, o URL HTTPS da base, esse SHA-256, `minimum_app_version` e as notas de alteração.
5. Publica os dois ficheiros juntos no ramo principal. O workflow CI valida o JSON, as traduções e a correspondência entre versão e SHA-256.

O URL atual da base tem de ser `https://raw.githubusercontent.com/asomimlrxd/PS5-Jailbreak-Doctor/main/knowledge_base.json`. O atualizador rejeita URLs fora do repositório esperado, checksum incorreto, JSON inválido, IDs duplicados e regex que não compile.

## Segurança e privacidade

A opção **Verificar scanner** usa apenas os endpoints de leitura `/api/v1/settings` e `/api/v1/manual/list` documentados no ShadowMountPlus 1.7. Não executa `/api/v1/scan`, não escreve definições e não altera origens. A aplicação verifica as capacidades anunciadas pelo endpoint `/api/v1/version` e trata endpoints ausentes como indisponíveis em vez de os interpretar como falha da ligação.

- A verificação só é iniciada depois de o utilizador escolher a ação no menu.
- O atualizador transfere apenas o manifesto e a base de conhecimento; não envia logs, relatórios, IP da PS5, nem dados de utilizador.
- A nova base é validada e escrita de forma atómica numa pasta de dados do utilizador.
- Antes da substituição, a base ativa é copiada para um backup local. Mantêm-se até cinco cópias e existe a opção de restaurar a mais recente.
- A verificação SHA-256 deteta corrupção/mismatch em relação ao manifesto publicado; não é uma assinatura digital do autor. A confiança continua a depender do HTTPS e do repositório de origem configurado.
- O executável não é atualizado por este mecanismo. Atualizações do código continuam a ser publicadas como releases do projeto.

## Connection relay (0.8.2)

The recommended path is now **ELF relay**, not manual editing of `/data/shadowmount/config.ini`. The Windows app can send the included `PS5JailbreakDoctorRelay.elf` to a compatible payload loader (usually TCP `9021`), then connect to the relay on TCP `10102`. Relay discovery uses UDP `10103`; if broadcast is blocked, the app attempts the saved console IP directly. A first-time installation still needs the PS5's current IP to send the ELF if no relay is already running.

The relay reads `api_bind_address`, `api_port`, and `api_enabled` but does not write any config. If the API is bound to a specific console address or a non-default port, it tries to create the `127.0.0.1:10101` alias required by the built-in launcher. If `api_enabled=0`, the relay stops rather than enabling it invisibly. The payload needs to be loaded again after a full reboot unless an existing autoloader is configured.

The relay's LAN socket only forwards the five read-only endpoints documented in `ps5-relay/README.md`. It has no authentication; use trusted private LAN only, and do not forward relay or API ports to the Internet. The payload is built by the GitHub Actions workflow using the pinned official PS5 Payload SDK v0.44. Verify CI and test the exact console/ShadowMountPlus build before publishing a stable release.

## Previous connection setup note (0.8.1)

For the ShadowMountPlus LAN API, use `api_bind_address=0.0.0.0` in `/data/shadowmount/config.ini` rather than binding the listener to the console's specific LAN IP. Enter that IP in the Doctor client only. The API is unauthenticated; only enable LAN access on a trusted private network and never forward the port to the Internet.
