# NovaPlay V 0.2.0 — TV aberta e clássicos

Protótipo web gratuito com canais abertos e acervo de cinema clássico.

## Conteúdo incorporado

- **4 filmes** de arquivo com domínio público indicado na página de origem no Wikimedia Commons.
- **10 episódios** de seriados antigos (9 capítulos de *The Perils of Pauline* de 1914 e 1 capítulo de *The Phantom Empire* de 1935).
- **6 emissoras**: TV Câmara (embed disponibilizado oficialmente), TV Brasil, TV Cultura, TV Senado, TV Assembleia MT e Canal Gov. Estes cinco últimos são atalhos para os próprios portais oficiais, sem retransmissão da NovaPlay.
- Busca, categorias, favoritos no dispositivo e PWA.

Os vídeos são buscados diretamente no Wikimedia Commons e podem não funcionar em alguns navegadores/conexões. Há link de fallback para a página original em cada player. Não hospedar espelhos dos vídeos sem verificar os direitos das versões específicas, inclusive trilhas sonoras, restaurações e adaptações. As licenças e prazos de proteção devem ser confirmados antes de comercializar.

**Base legal brasileira:** Lei 9.610/1998, art. 44 (70 anos a partir de 1º janeiro após divulgação das obras audiovisuais); outros direitos conexos podem existir. Os filmes são originalmente mudos ou em língua estrangeira e podem não ter dublagem ou legendas.

## Publicação

**Versão que usamos agora:** https://novabytesolucoes.com.br/novaplay/

O repositório independente \`NovaPlay\` possui workflow de publicação preparado, mas o GitHub Pages da conta ainda não foi ativado administrativamente. A URL \`...github.io/NovaPlay/\` não é uma publicação confirmada.

## Teste local

\`\`\`bash
python -m http.server 8000
\`\`\`

Acesse http://localhost:8000. Para funcionar em Android como PWA, use HTTPS.

## Próximas etapas

Catalogação, playlists com licença expressa, acompanhamento da disponibilidade, administração e eventualmente contas de usuário. Canais oficiais devem continuar gratuitos, sem paywall e sem retransmissão, a menos que haja autorização expressa.
