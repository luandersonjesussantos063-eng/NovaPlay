# NovaPlay — Protótipo IPTV e streaming

Web app experimental para TV ao vivo, filmes e séries, com layout adaptado ao celular e player de vídeo HLS.

## Funcionalidades implementadas

- Navegação em Início, TV, Filmes, Séries e Favoritos.
- Busca e filtro de conteúdos.
- Player HLS (nativo / hls.js).
- Favoritos salvos somente no navegador.
- Manifest e service worker básicos (PWA).
- Catálogo com **3 fluxos públicos de demonstração**, sujeitos à disponibilidade dos respectivos servidores.

**Não implementado:** login, cobrança, assinatura premium, streaming privado, canais comerciais, licenciamento ou sincronização de dados.

## Rodar localmente

Abra um servidor HTTP nesta pasta:

```
python -m http.server 8000
```

Visite http://localhost:8000/. A biblioteca de reprodução HLS e os fluxos exigem acesso à internet.

## Publicar no GitHub Pages

No repositório, abra Settings → Pages → Build and deployment → Source → **GitHub Actions**. O workflow de publicação deste repositório publica automaticamente o conteúdo da branch main. A implantação também pode ser acionada manualmente em Actions.

URL esperada depois de ativar e concluir o deployment:
https://luandersonjesussantos063-eng.github.io/NovaPlay/

## Uso comercial

Antes de vender acesso, obtenha direitos de distribuição e implemente autenticação, verificação de assinatura no servidor, links de transmissão protegidos, privacidade e pagamentos com webhook verificado. Não coloque tokens secretos, listas privadas ou chaves do Mercado Pago no front-end.
