# Documentação – Backup Automatizado Safion (Nextcloud + n8n)

**Versão:** 1.1  
**Última atualização:** 2026-01-06

---

## 1. Visão Geral

Esta documentação descreve a configuração **atualizada** do backup automatizado da infraestrutura Safion na VPS Hostinger (Ubuntu 24.04 + Docker), incluindo:

- Nextcloud (dados + banco PostgreSQL)
- n8n (dados + banco SQLite)
- Envio offsite para Google Drive
- Agendamento automático via Cron
- **Política de retenção local (10 dias)**

A solução utiliza **Cron + Rclone**, com execução diária noturna e retenção controlada localmente.

---

## 2. Escopo do Backup

### Nextcloud

- **Dados dos usuários**
  - `/var/www/html/data`
- **Configuração**
  - `/var/www/html/config/config.php`
- **Banco de dados**
  - PostgreSQL (dump lógico via `pg_dump`)
  - Container: `nextcloud-db`

### n8n

- **Diretório persistente completo**
  - `/home/node/.n8n`
- **Banco**
  - SQLite (`database.sqlite`)
- Inclui workflows, credenciais e execuções

---

## 3. Destino dos Backups

### Local (VPS)

```text
/opt/backups/
 ├── work/       # Área temporária
 └── archives/   # Backups finais (.tar.zst)
```

### Offsite

- **Google Drive**
- Rclone remote: `gdrive-backup`
- Pasta: `infra-backups/`
- **Sem política de retenção offsite (por decisão atual)**

---

## 4. Script de Backup

### Localização

```text
/usr/local/bin/backup-infra.sh
```

### Funções

1. Ativa maintenance mode do Nextcloud
2. Executa dump do PostgreSQL
3. Copia dados e configuração do Nextcloud
4. Copia dados persistentes do n8n
5. Compacta tudo em `.tar.zst` (tar + zstd)
6. Envia o arquivo ao Google Drive
7. Desativa maintenance mode

---

## 5. Agendamentos (Cron)

### Backup diário

- **Horário:** 02:00
- **Usuário:** root
- **Log:** `/var/log/backup-infra/cron.log`

```cron
0 2 * * * /usr/local/bin/backup-infra.sh >> /var/log/backup-infra/cron.log 2>&1
```

### Tarefas internas do Nextcloud (obrigatórias)

```cron
*/5 * * * * docker exec -u www-data nextcloud-app php -f /var/www/html/cron.php > /dev/null 2>&1
```

---

## 6. Política de Retenção Local (NOVA)

### Objetivo

Evitar crescimento ilimitado do disco da VPS, mantendo backups locais apenas para restores rápidos.

### Configuração

- **Retenção local:** 10 dias
- **Escopo:** somente arquivos `.tar.zst`
- **Diretório:** `/opt/backups/archives`
- **Offsite:** não afetado

### Cron de limpeza

- **Horário:** 03:30 (após o backup)
- **Log:** `/var/log/backup-infra/cleanup.log`

```cron
30 3 * * * find /opt/backups/archives -type f -name "*.tar.zst" -mtime +10 -delete >> /var/log/backup-infra/cleanup.log 2>&1
```

### Observações

- O log `cleanup.log` é criado somente quando a limpeza roda pela primeira vez
- Backups recentes nunca são removidos
- Backups no Google Drive permanecem intactos

---

## 7. Logs Importantes

```text
/var/log/backup-infra/cron.log    # Execução do backup
/var/log/backup-infra/cleanup.log # Execução da limpeza
```

Verificação:

```bash
tail -n 50 /var/log/backup-infra/cron.log
tail -n 50 /var/log/backup-infra/cleanup.log
```

---

## 8. Restore / Disaster Recovery (Resumo)

1. Baixar backup do Google Drive
2. Descompactar `.tar.zst`
3. Restaurar dados do Nextcloud
4. Restaurar banco PostgreSQL
5. Restaurar dados do n8n
6. Subir containers e validar

> Restore completo deve ser testado periodicamente em ambiente de validação.

---

## 9. Status Atual

- Backup diário: ✅
- Backup offsite: ✅
- Retenção local (10 dias): ✅
- Retenção offsite: ❌ (não configurada por decisão)
- Restore documentado: ✅

---

## 10. Próximas Evoluções Recomendadas

- Criptografia dos backups no Google Drive (`rclone crypt`)
- Retenção offsite controlada
- Alertas de falha de backup ou disco cheio
- Teste de restore trimestral

---

**Documento oficial de referência da Safion – Infraestrutura e Backup**
