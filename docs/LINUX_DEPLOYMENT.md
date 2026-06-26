# Linux / Docker 部署说明

## Ubuntu 环境

建议使用 Ubuntu 22.04 或 24.04，安装 Python 3.11、Git、Docker、Docker Compose 和 Nginx。

## Python venv 部署

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## .env

```text
DATABASE_PATH=./business_demo.db
FEISHU_WEBHOOK_URL=
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
MYSQL_HOST=mysql
MYSQL_DATABASE=flowpilot
MYSQL_USER=flowpilot
MYSQL_PASSWORD=flowpilot_demo
```

## Docker Compose

```bash
docker compose up -d --build
docker compose logs -f app
```

## Nginx 反向代理

把域名代理到本机 `127.0.0.1:8000`，并使用 Certbot 配置 HTTPS。

## systemd 常驻运行

非 Docker 部署可以创建 systemd service，设置 `WorkingDirectory`、`EnvironmentFile` 和 `ExecStart`，再用 `systemctl enable --now` 管理进程。

## 日志排查

- `docker compose logs -f app`
- `docker compose logs -f mysql`
- `journalctl -u flowpilot -f`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`

## Webhook 安全配置

生产环境应校验签名或 Token，限制来源 IP，不要把 Webhook URL、API Key 写入 Git 仓库。
