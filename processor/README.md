# Processador de vídeos NPlay (R2 → FFmpeg → HLS → R2)

O processador recebe somente uma **chave de objeto já armazenado** no bucket privado R2. Não baixa torrents ou URLs de terceiros. Use apenas vídeos que a NPlay tenha autorização para distribuir.

## Requisitos
- Docker (ou Python 3.12, FFmpeg e dependências de requirements.txt)
- Credenciais **R2 S3 API** com permissão limitada ao bucket `nplay-filmes`
- Espaço temporário de pelo menos 2–3 vezes o tamanho do vídeo, CPU e RAM suficientes

## Construção
```sh
docker build -t nplay-processor ./processor
```

## Execução sob demanda
```sh
docker run --rm --env-file ./processor/.env -v nplay-tmp:/tmp nplay-processor \
  --input-key "ID-DO-ADMIN/ARQUIVO.mp4" \
  --output-prefix "hls/ID-DO-FILME"
```

O arquivo `processor/.env` deve conter:
```dotenv
R2_ACCOUNT_ID=SEU_ACCOUNT_ID
R2_BUCKET=nplay-filmes
R2_ACCESS_KEY_ID=SUA_CHAVE_R2
R2_SECRET_ACCESS_KEY=SEU_SEGREDO_R2
```

**Nunca publique esse .env no GitHub.** O processador não precisa de chaves Supabase. O resultado é `hls/ID-DO-FILME/index.m3u8`, ainda **privado** no R2.

## Próximos passos antes de disponibilizar a reprodução
1. Configurar um executor Docker (máquina local ou servidor sob demanda).
2. Criar credenciais R2 restritas e armazená-las apenas como segredos do executor.
3. Testar com um vídeo pequeno autorizado e conferir áudio, imagem e playlist.
4. Implementar uma API de reprodução autenticada para manifest e segmentos HLS.
5. Integrar a fila de processamento e estados ao painel NPlay.

Este repositório **não** implanta automaticamente um servidor, não expõe os vídeos e não cria despesas de computação sem sua aprovação.
