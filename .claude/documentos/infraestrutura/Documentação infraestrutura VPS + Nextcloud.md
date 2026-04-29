DOCUMENTAÇÃO DA ARQUITETURA ATUAL – VPS HOSTINGER (Ubuntu 24.04 + Docker)

(Versão inicial – pode ser expandida conforme novas informações)

1. Visão Geral da Arquitetura

A VPS da Hostinger hospeda uma arquitetura composta por múltiplos serviços containerizados utilizando Docker. O ambiente fornece:

Plataforma de colaboração Nextcloud

Ferramenta de automação de workflows n8n

Reverse proxy e gerenciador de certificados Traefik

Banco de dados PostgreSQL para aplicações separadas

Caches Redis independentes

Aplicação personalizada Evolution API

Essa arquitetura segue boas práticas de isolamento de serviços e modularidade, permitindo escalabilidade, manutenção facilitada e atualizações independentes.

2. Especificações da VPS
   Componente Valor
   Provedor Hostinger
   SO Ubuntu 24.04.2 LTS
   Kernel 6.8.0-88-generic x86_64
   Armazenamento 95.82 GB (41.1% utilizado)
   Memória RAM ~16% utilizada
   Swap 0% utilizada
   CPU Load 0.06 (estável e leve)
   IP Público IPv4 31.97.253.130
   IPv6 2a02:4780:14:f387::1
   Usuários logados 1
   Processos zumbis 1
   Atualizações pendentes 70 updates (2 de segurança)
3. Arquitetura em Containers (Docker)

A seguir, a documentação detalhada de cada container ativo, sua função, portas e dependências.

3.1 Diagramas de Arquitetura
🔷 Fluxo Geral dos Serviços
┌───────── Traefik (Reverse Proxy) ─────────┐
│ Portas 80 / 443 │
│ │
└──────→ encaminha requisições →──────────────┘
│
┌───────────┴───────────┐
│ │
Nextcloud (App & Cron) Evolution API
│ │
┌───────┴────────┐ ┌────┴─────┐
│ │ │ │
Nextcloud DB Nextcloud Redis Evolution DB
│
└── n8n (integrações e automações)

Se quiser, posso gerar um diagrama visual real (PNG/SVG).

4. Descrição Completa dos Containers
   4.1 Nextcloud Stack
   4.1.1 nextcloud-app

Função: aplicação principal e interface web do Nextcloud.

Porta: 80/tcp

Responsável por:

autenticação

arquivos e sincronização

gerenciamento de usuários

apps e configurações

4.1.2 nextcloud-cron

Executa tarefas internas programadas:

limpeza de arquivos temporários

indexação

manutenção do banco

verificações de integridade

4.1.3 nextcloud-db (PostgreSQL 16)

Banco de dados oficial da instância Nextcloud.

Armazena: usuários, permissões, metadados de arquivos, configs e apps.

4.1.4 nextcloud-redis / root-redis-1

Redis auxilia nas operações:

cache de consultas

file locking

sessão de usuários

Melhora significativamente a performance.

4.2 Evolution API Stack
4.2.1 evolution_api

Porta: 8080/tcp

Contém uma aplicação personalizada (backend/API).

Comunicação com banco próprio: postgres_evolution.

4.2.2 postgres_evolution

Banco PostgreSQL dedicado para a aplicação Evolution.

Segue boa prática de separação de bancos por serviço.

4.3 Serviços de Infraestrutura
4.3.1 Traefik v3

Reverse proxy moderno com suporte a:

TLS/SSL automatizado (Let's Encrypt)

roteamento de hosts e subdomínios

dashboards

middlewares (redirecionamentos, rate-limit, autenticação)

Portas expostas:

80 → HTTP

443 → HTTPS

É o componente que publica o Nextcloud e demais serviços para a internet.

4.4 n8n – Automação
4.4.1 root-n8n-1

Porta interna: 5678

Ferramenta de workflow no-code.

Pode integrar:

Nextcloud

Evolution API

APIs externas

bancos de dados

Utilizado para automatizar operações e conectar sistemas.

5. Recursos e Comunicação Entre Containers
   ● Redes Docker

Os containers provavelmente utilizam uma rede bridge criada automaticamente ou definida no docker-compose.

● Conectividade

Nextcloud-app ⇄ nextcloud-db

Nextcloud-app ⇄ nextcloud-redis

nextcloud-cron ⇄ nextcloud-app (mesmo volume)

Evolution-api ⇄ postgres_evolution

Traefik ⇄ nextcloud-app / evolution_api / n8n

● Volumes Persistentes

Recomendado listar no compose (posso gerar essa seção se enviar seu docker-compose.yml).

6. Checklist de Segurança do Ambiente (atual)

Com base no print:

Atualizações pendentes precisam ser aplicadas

Processo zumbi deve ser investigado

Verificar firewall (UFW ou nftables)

Confirmar renovação automática dos certificados SSL do Traefik

Configurar backup entre:

dados do Nextcloud (/var/www/html/data)

volumes Docker

bancos de dados PostgreSQL

Se quiser, posso gerar uma política de backup passo a passo.

7. Pontos Fortes da Arquitetura

Uso eficiente de containerização

Banco de dados isolado por aplicação

Boas práticas de cache (Redis)

Proxy reverso robusto (Traefik)

Baixo uso de recursos

Flexível e escalável

8. Possíveis Melhorias Futuras

Implementação de docker-compose.yml documentado

Backup automatizado via n8n/cron

Hardened security:

fail2ban

bloqueio de SSH por chave

desabilitar root login

Monitoramento:

Grafana + Prometheus

Healthchecks para containers

Logs centralizados

9. Apêndice — Lista de Containers (reprodução do print)
   CONTAINER ID IMAGE COMMAND PORTS
   ...
   e5f3d... nextcloud:28 "/entrypoint.sh apac…" 80/tcp
   3c0...
   c0f...
   ...
   918e0... traefik:v3.0 "traefik…" 80->80, 443->443
   ...
   e8a8... n8nio/n8n:latest "tini -- /docker-ent…" 5678/tcp
