# PS5 Game Compatibility Atlas — Português (Portugal)

O **PS5 Game Compatibility Atlas** organiza relatos públicos de jogos PS5 em ambientes homebrew, cruzando firmware, formato, armazenamento, sintomas, duração do teste e fontes originais.

## Começar

Executa na pasta do projeto:

```bash
python -m http.server 8000
```

Abre depois `http://localhost:8000`. O site principal não precisa de backend. O separador de downloads consulta APIs públicas do catálogo homebrew e GitHub quando o utilizador pede; se um serviço bloquear CORS, a página oficial continua acessível.

## O que contém

- 83 registos de teste e 46 nomes de jogos/títulos.
- 18 fontes públicas e 7 guias de formato.
- Pesquisa e filtros por firmware, formato, armazenamento e estado.
- Português de Portugal e inglês, com tema escuro e interface adaptável.
- Novo separador **Downloads & fontes** para aplicações homebrew publicadas em `homebrew.page` e releases oficiais do GitHub.
- Fila local de downloads de homebrew com progresso, pausa/retoma quando suportada e verificação SHA-256 antes de guardar o ficheiro. A assinatura Ed25519 do manifesto do catálogo e os hashes dos ficheiros JSON são verificados antes de usar os metadados.
- Conectores para as páginas oficiais de Orbit Store, Spectrum Library e PS5Library.
- Fontes personalizadas guardadas localmente; fornecedores como Vikingfile são abertos manualmente, sem scraping nem bypass de verificações.
- Downloads de jogos comerciais não são indexados nem distribuídos pelo Atlas.
- Formulário de contribuição local: os dados ficam no teu navegador e podem ser exportados para JSON. Não são enviados para um servidor.
- Exportação dos registos curados para CSV ou JSON.

## Interpretação

Um registo descreve uma configuração e uma observação — não define o estado universal de um jogo. «Teste curto» não equivale a conclusão, e resultados contraditórios permanecem separados. A qualidade da evidência descreve quão bem o relato está documentado, não uma probabilidade estatística de sucesso.

A documentação atual do ShadowMountPlus recomenda `.ffpkg`/UFS para uso geral, apresenta `.exfat` como opção de compatibilidade para alguns títulos e classifica PFS (`.ffpfs`/`.ffpfsc`) como experimental. Os resultados específicos por jogo podem divergir destas indicações.

Consulta `METHODOLOGY.md` e `DOWNLOADS_SOURCES.md` para conhecer as fontes/limitações e `CONTRIBUTING.md` antes de introduzir novos resultados ou conectores.
