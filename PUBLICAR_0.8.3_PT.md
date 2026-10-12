# Publicar a versão 0.8.3 — PS5 Jailbreak Doctor

1. Extrai todo o conteúdo do ZIP para uma pasta nova.
2. Abre o GitHub do projeto `asomimlrxd/PS5-Jailbreak-Doctor`.
3. Atualiza os ficheiros do projeto com os ficheiros deste pacote, mantendo a pasta `.github/workflows`. Não existe qualquer relay ELF nesta versão.
4. Confirma que `app.py`, `i18n.py`, `doctor_core.py`, `knowledge_base.json`, `updates.py` e `updates.json` ficam todos na raiz.
5. Faz commit/push para `main` e abre **Actions**. Espera que os testes e a compilação para Windows terminem com sucesso.
6. Testa o artifact gerado: abre a aplicação, alterna PT/EN e temas, carrega o exemplo, importa um log e verifica a ligação à PS5.
7. Só depois cria uma release e anexa `PS5JailbreakDoctor.exe` e o respetivo `.sha256`.

A primeira compilação tem de ocorrer no GitHub Actions/Windows. O ZIP contém código-fonte; não afirma que o executável foi compilado ou testado numa PS5.
