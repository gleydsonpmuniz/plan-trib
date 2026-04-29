# DNS Setup — plantrib.safion.com.br

## Registro a criar

| Campo | Valor |
|-------|-------|
| Tipo | A |
| Nome | plantrib |
| Domínio | safion.com.br |
| Valor | 31.97.253.130 |
| TTL | 300 (5 min) |

## Onde criar

Painel DNS do provedor de domínio do `safion.com.br` (Hostinger ou Registro.br,
conforme contratado). Após criar, validar com:

```bash
dig +short plantrib.safion.com.br
# Deve retornar: 31.97.253.130
```

## TLS (automático)

Após o DNS resolver, o Traefik na VPS detectará o roteador (label
`traefik.http.routers.plan-trib-web.rule=Host(plantrib.safion.com.br)`)
e solicitará certificado Let's Encrypt automaticamente via ACME tlschallenge.

Tempo estimado: ~30s após o primeiro `docker compose up` se o DNS estiver
propagado. Verificar com:

```bash
curl -I https://plantrib.safion.com.br
# Deve retornar 200 ou 401 (depende da rota), nunca erro de TLS
```
