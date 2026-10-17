# Publicar o PS5 Jailbreak Doctor 1.04

## O que inclui
- Diagnóstico de ligação à API HTTP do ShadowMountPlus, exclusivamente por endpoints de leitura.
- Comparação local entre sessões de logs.
- Exportação de relatório de partilha com anonimização forçada e caminhos reduzidos a nomes de ficheiro.
- Duas novas regras contextuais na base de conhecimento e fontes atualizadas para ShadowMountPlus 1.7beta5.
- Paletas visuais revistas e novos testes de regressão.

## Validar antes de distribuir
1. Confirma no GitHub Actions que o workflow **Validate PS5 Jailbreak Doctor** passou.
2. Confirma que **Build and publish PS5 Jailbreak Doctor** compilou `PS5JailbreakDoctor.exe` e calculou o checksum SHA-256.
3. Testa o executável no Windows.
4. Se possível, testa a ligação com a tua PS5 e confirma que a recolha de logs funciona. O projeto não altera `config.ini`.
5. Confirma que os novos comandos de comparar sessões e exportar relatório anonimizado funcionam em PT e EN.

## Release draft
A tag é `v1.04` e a release deve permanecer em **draft** até adicionares o executável testado e o ficheiro `PS5JailbreakDoctor.exe.sha256`. A automatização não deve carregar nem substituir o executável por ti.

## Nota sobre ligações
A API do ShadowMountPlus usa `127.0.0.1:10101` como endereço predefinido, o que só permite ligações locais na própria PS5. Para o Doctor no Windows, a API precisa de estar acessível na rede local. Esta versão explica o problema e diagnostica a ligação, mas não altera configurações da consola nem promete resolver automaticamente uma API que não esteja exposta à LAN.

## Privacidade
A análise e comparação de logs são locais. A exportação de partilha aplica redação e remove diretórios locais das origens, mas deves rever o relatório manualmente antes de o partilhares.
