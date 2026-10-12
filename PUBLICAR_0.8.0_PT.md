# Como instalar e publicar a versão 0.8.0

Este ZIP contém o código-fonte completo do PS5 Jailbreak Doctor 0.8.0. Não contém um executável Windows já compilado.

## Substituir a pasta local do projeto

1. Guarda uma cópia de segurança da tua pasta atual do projeto.
2. Extrai `PS5-Jailbreak-Doctor-0.8.0.zip` para uma pasta temporária.
3. Copia o conteúdo da pasta `PS5-Jailbreak-Doctor-0.8.0` para a pasta local do teu repositório, mantendo a estrutura das pastas, incluindo `.github`, `docs` e `tests`.
4. Revê as alterações antes de as publicar. Se usares GitHub Desktop, confirma a lista de ficheiros alterados, cria um commit e faz push para o ramo principal.
5. Abre o separador **Actions** do GitHub e confirma que o workflow **Build and publish PS5 Homebrew Doctor** terminou com sucesso.
6. Só depois de passar o workflow, publica a release e testa o `.exe` num Windows. O executável não foi compilado nem testado neste ambiente Linux.

## Importante para o atualizador

A opção «Atualizar base de diagnósticos» consulta `updates.json` e `knowledge_base.json` no ramo `main` deste repositório. Para funcionar, publica os dois ficheiros juntos, juntamente com o código `updates.py` e as alterações do motor de diagnóstico. O manifesto contém o SHA-256 exato da base; não o alteres manualmente sem recalcular esse valor.

## O que a aplicação faz com os endpoints do scanner

A opção «Verificar scanner» consulta apenas `/api/v1/settings` e `/api/v1/manual/list`, quando a versão do ShadowMountPlus anuncia essas capacidades. Não chama `/api/v1/scan`, não muda configurações nem adiciona/remove origens. A API do ShadowMountPlus não tem autenticação na integração documentada; utiliza-a apenas numa rede local de confiança e nunca exponhas a porta diretamente à Internet.
