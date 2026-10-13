# Contribuir com resultados

O formulário dentro do site guarda os teus registos **apenas no navegador**. Não existe envio automático nem backend. Podes exportar o JSON e preparar uma contribuição manual após revisão.

## Campos recomendados

Inclui, quando conhecidos:

- nome do jogo e Title ID;
- firmware e modelo de PS5;
- versão do jogo e dos payloads/ferramentas;
- formato exatamente como declarado pela fonte;
- localização exata: SSD interno original, SSD M.2 de expansão, SSD externo, USB flash ou HDD externo;
- resultado observado, sintomas e duração do teste;
- resolução e se foi efetivamente confirmada;
- URL pública original e data da observação.

Não inventes valores desconhecidos. Usa «Não indicado»/`unknown` sempre que necessário.

## Regras editoriais

1. A fonte tem de ser pública e acessível.
2. Usa resumos próprios e curtos. Não copies comentários extensos.
3. Um teste de poucos minutos deve ser `playable_short`, não `completed`.
4. Não agregues formatos ou localizações diferentes num único resultado se tiverem resultados distintos.
5. Mantém relatos contraditórios como registos separados.
6. Não inferir firmware do autor de um comentário a partir do contexto da thread sem assinalar essa incerteza.
7. Não atribuir causalidade definitiva apenas porque uma alteração precedeu a resolução.
8. Não adicionar links para dumps, jogos, patches ou fontes de distribuição não autorizada.
9. Para o separador Downloads, apenas integrar catálogos de homebrew/repositórios que publiquem a origem, licença e hash quando disponível. Não raspar páginas de file-hosting, não contornar CAPTCHA/logins nem indexar catálogos de jogos comerciais.
10. Um hash corresponde à integridade contra o valor publicado; não significa que o ficheiro foi auditado ou é seguro.
11. Todos os registos devem ter `summary_pt` e `summary_en`, uma referência de fonte válida e um ID único.
12. Depois de editar `build_data.py`, executa o gerador, os testes e `node --check app.js`.
