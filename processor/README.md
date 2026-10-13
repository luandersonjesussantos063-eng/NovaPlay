# Processador NPlay sem chaves S3

O processador usa **FFmpeg no Docker** e transfere os vídeos pelo **Worker Cloudflare** com binding R2 `VIDEOS`. O Worker exige autenticação Supabase de um administrador NPlay. **Não use mais R2_ACCESS_KEY_ID ou R2_SECRET_ACCESS_KEY.**

## Preparação

1. Revogue as chaves R2 anteriormente expostas.
2. Faça login no painel NPlay como administrador. Obtenha um **access token Supabase válido** somente no seu ambiente local; não envie o token por chat nem faça commit.
3. Descubra seu UUID de usuário administrador e a URL pública do Worker `nplay-r2-api` na Cloudflare.
4. Crie `processor/.env` **localmente** com:

```dotenv
NPLAY_WORKER_URL=https://SEU-WORKER.workers.dev
NPLAY_ADMIN_USER_ID=UUID-DO-ADMIN
NPLAY_ADMIN_ACCESS_TOKEN=TOKEN-DE-ACESSO-SUPABASE
```

O token Supabase expira e precisará ser renovado; este é um fluxo inicial de processamento manual, não um serviço contínuo.

## Execução

Na pasta raiz do repositório:

```powershell
docker build -t nplay-processor ./processor
docker run --rm --env-file .\processor\.env nplay-processor --help
docker run --rm --env-file .\processor\.env -v nplay-tmp:/tmp nplay-processor --input-key "UUID-DO-ADMIN/VIDEO.mp4" --output-prefix "hls/UUID-DO-ADMIN/ID-DO-FILME"
```

A entrada precisa existir no bucket `nplay-filmes`, no prefixo do administrador, e ser conteúdo autorizado. A saída fica privada em `hls/UUID-DO-ADMIN/ID-DO-FILME/index.m3u8`.

## Estado

O Worker tem as rotas autenticadas `GET /processor/source?key=...` e `PUT /processor/output?key=...`. O Dockerfile usa `process_worker.py` por padrão. O antigo `process.py` permanece no repositório apenas para referência. **A reprodução HLS pelo site e a fila de processamento ainda precisam ser integradas.**
