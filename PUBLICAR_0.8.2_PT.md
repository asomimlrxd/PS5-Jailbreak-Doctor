# Publicar o PS5 Jailbreak Doctor 0.8.2

## O que muda

A versão 0.8.2 introduz o `PS5JailbreakDoctorRelay.elf`, um payload auxiliar experimental para recolher logs sem editar `/data/shadowmount/config.ini`. O ELF lê a configuração atual, faz a ponte para a API HTTP do ShadowMountPlus e cria um alias local em `127.0.0.1:10101` quando é necessário para o launcher. O tráfego remoto fica limitado a endpoints de leitura.

## Publicar no GitHub

1. Faz uma cópia de segurança do repositório local atual.
2. Extrai o ZIP da versão 0.8.2 para uma pasta temporária.
3. Copia os ficheiros atualizados para o clone local do repositório, mantendo os ficheiros de documentação/imagens que não foram alterados. Inclui a pasta `ps5-relay`, o `relay_client.py`, o workflow, os testes, `app.py`, `i18n.py`, `doctor_core.py`, `knowledge_base.json`, `updates.json` e a documentação atualizada.
4. Revê `git diff` antes de publicar. Confirma em particular que não há IPs privados pessoais nem logs da tua consola em ficheiros de exemplo.
5. Faz commit numa branch com a mensagem `Add PS5 relay ELF for config-free connection`, envia-a para GitHub e abre um Pull Request para `main` (ou faz push direto se preferires manter o teu fluxo habitual).
6. No separador **Actions**, executa o workflow **Build and publish PS5 Homebrew Doctor**. A primeira tarefa descarrega o SDK oficial v0.44 e valida o checksum; depois compila o ELF. A segunda tarefa corre os testes Python e constrói o `.exe` do Windows com o ELF incorporado.
7. Só continua se ambas as tarefas terminarem com sucesso. Transfere os artifacts e guarda `PS5JailbreakDoctorRelay.elf`, os checksums e `PS5HomebrewDoctor.exe` para um teste local.
8. Testa primeiro a aplicação sem abrir/editar `config.ini`: confirma que o relay é carregado, que `GET`/leitura de versão e logs funcionam, e que a interface do ShadowMountPlus continua acessível. Faz também um reinício completo da PS5 e confirma que o Doctor consegue carregar o ELF novamente.
9. Publica uma Release `v0.8.2` apenas depois dos testes no equipamento. O workflow anexa o executável Windows, o ELF e os respetivos SHA-256 à Release.

## Como funciona a ligação

- Para a primeira ligação, o utilizador pode ter de introduzir o IP LAN atual da PS5 no Doctor. Esse IP é guardado apenas nas preferências locais.
- O loader de payloads tem de aceitar ELF por TCP `9021` (o padrão típico usado pelo workflow). Se não estiver ativo, o utilizador terá de ativar o loader ou carregar o ELF através do método já usado na consola.
- O relay usa TCP `10102` e UDP `10103`. Se a descoberta por broadcast estiver bloqueada, o Doctor tenta o IP guardado diretamente.
- O relay tem de ser carregado novamente após um reinício completo, a menos que o utilizador já tenha um autoloader configurado. Não cria nem modifica autoloaders.
- Se `api_enabled=0`, o ELF pára e notifica o utilizador. Não altera a configuração para ativar a API.

## Segurança e limitações

O relay não modifica o ficheiro de configuração e não utiliza o socket Unix privado do ShadowMountPlus. Pela LAN aceita clientes IPv4 de redes privadas e apenas as rotas `POST /api/v1/version`, `/api/v1/debug-log`, `/api/v1/kernel-log`, `/api/v1/settings` e `/api/v1/manual/list`. O serviço não tem autenticação: usa-o apenas numa LAN privada de confiança e nunca encaminhes as portas para a Internet.

O código C foi verificado localmente por sintaxe com o compilador C do host, e os testes unitários Python são executados localmente. A compilação SDK real, a entrega do payload pela porta 9021 e o comportamento do launcher têm de ser confirmados por GitHub Actions e teste na PS5 física. Não anunciar o ELF como estável antes disso.
