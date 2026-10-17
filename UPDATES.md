# Atualizações da base de diagnósticos

A aplicação não atualiza automaticamente o executável. O botão **Atualizar base de diagnósticos** consulta `updates.json` e, apenas após confirmação explícita, transfere a base de regras indicada.

## Publicar uma nova base

1. Atualiza `knowledge_base.json` e aumenta `database_version`.
2. Cada regra nova ou modificada deve incluir `translations.en` para `title`, `summary`, `fix_summary`, `applicability` (quando existirem) e o mesmo número de passos traduzidos que `steps`. As notas da `compatibility_matrix` também devem incluir `translations.en` para `title`, `summary` e `status`.
3. Calcula o SHA-256 dos bytes exatos do ficheiro final `knowledge_base.json`.
4. Atualiza `updates.json` com a nova versão, o URL HTTPS da base, esse SHA-256, `minimum_app_version` e as notas de alteração.
5. Publica os dois ficheiros juntos no ramo principal. O workflow CI valida o JSON, as traduções e a correspondência entre versão e SHA-256.

O URL atual da base tem de ser `https://raw.githubusercontent.com/asomimlrxd/PS5-Jailbreak-Doctor/main/knowledge_base.json`. O atualizador rejeita URLs fora do repositório esperado, checksum incorreto, JSON inválido, IDs duplicados e regex que não compile.

## Base publicada na versão 1.04

A base fornecida com a versão 1.04 usa `database_version: 2026.10.17.1`. Inclui 32 regras e 5 notas de compatibilidade, com novos diagnósticos contextuais para o listener HTTP que deixa de responder e varreduras que ficam em fila depois de fechar um jogo. As issues #152/#153 e a PR #163 estão marcadas como casos abertos/proposta; não são apresentadas como correções publicadas.

## Segurança e privacidade

A opção **Verificar scanner** usa apenas os endpoints de leitura `/api/v1/settings` e `/api/v1/manual/list` documentados no ShadowMountPlus 1.7. Não executa `/api/v1/scan`, não escreve definições e não altera origens. A aplicação verifica as capacidades anunciadas pelo endpoint `/api/v1/version` e trata endpoints ausentes como indisponíveis em vez de os interpretar como falha da ligação.

- A verificação só é iniciada depois de o utilizador escolher a ação no menu.
- O atualizador transfere apenas o manifesto e a base de conhecimento; não envia logs, relatórios, IP da PS5, nem dados de utilizador.
- A nova base é validada e escrita de forma atómica numa pasta de dados do utilizador.
- Antes da substituição, a base ativa é copiada para um backup local. Mantêm-se até cinco cópias e existe a opção de restaurar a mais recente.
- A verificação SHA-256 deteta corrupção/mismatch em relação ao manifesto publicado; não é uma assinatura digital do autor. A confiança continua a depender do HTTPS e do repositório de origem configurado.
- O executável não é atualizado por este mecanismo. Atualizações do código continuam a ser publicadas como releases do projeto.
