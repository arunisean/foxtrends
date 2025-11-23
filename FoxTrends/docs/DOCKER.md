# FoxTrends Docker 部署指南

## 目录

1. [快速开始](#快速开始)
2. [配置说明](#配置说明)
3. [部署选项](#部署选项)
4. [管理和维护](#管理和维护)
5. [故障排查](#故障排查)

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 10GB 可用磁盘空间

### 安装 Docker

**Ubuntu/Debian**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS**:
```bash
brew install --cask docker
```

**Windows**:
下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 快速部署

1. **克隆项目**

```bash
git clone https://github.com/your-repo/FoxTrends.git
cd FoxTrends
```

2. **配置环境变量**

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下必需项：

```bash
# 数据库密码
DB_PASSWORD=your_secure_password

# 应用密钥
SECRET_KEY=your_secret_key_here

# LLM API 密钥
INSIGHT_AGENT_LLM_API_KEY=sk-xxx
CONTENT_AGENT_LLM_API_KEY=sk-xxx
FORUM_ENGINE_LLM_API_KEY=sk-xxx

# Reddit API（如果需要）
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# GitHub API（如果需要）
GITHUB_TOKEN=ghp_xxx
```

3. **启动服务**

```bash
docker-compose up -d
```

4. **查看日志**

```bash
docker-compose logs -f foxtrends
```

5. **访问应用**

打开浏览器访问: http://localhost:5000

---

## 配置说明

### 环境变量

所有配置通过环境变量传递，可以在 `.env` 文件中设置：

#### 必需配置

```bash
# 数据库密码
DB_PASSWORD=your_secure_password

# 应用密钥（用于 session 加密）
SECRET_KEY=your_secret_key_here

# LLM API 密钥
INSIGHT_AGENT_LLM_API_KEY=sk-xxx
CONTENT_AGENT_LLM_API_KEY=sk-xxx
FORUM_ENGINE_LLM_API_KEY=sk-xxx
```

#### 可选配置

```bash
# LLM 模型配置
INSIGHT_AGENT_LLM_BASE_URL=https://api.moonshot.cn/v1
INSIGHT_AGENT_LLM_MODEL=moonshot-v1-8k

# 日志级别
LOG_LEVEL=INFO

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=FoxTrends/1.0

# GitHub API
GITHUB_TOKEN=ghp_xxx
```

### 数据持久化

Docker Compose 配置了以下数据卷：

- `postgres_data`: PostgreSQL 数据库数据
- `./logs`: 应用日志
- `./final_reports`: 生成的报告

数据会持久化保存，即使容器重启也不会丢失。

---

## 部署选项

### 选项 1: 标准部署（PostgreSQL）

使用 PostgreSQL 作为数据库，适合生产环境：

```bash
docker-compose up -d
```

服务包括：
- `foxtrends`: FoxTrends 应用
- `postgres`: PostgreSQL 数据库

### 选项 2: 包含 Redis 缓存

启用 Redis 缓存以提高性能：

```bash
docker-compose --profile with-redis up -d
```

服务包括：
- `foxtrends`: FoxTrends 应用
- `postgres`: PostgreSQL 数据库
- `redis`: Redis 缓存

### 选项 3: 仅应用（使用外部数据库）

如果你已有 PostgreSQL 数据库，可以只运行应用：

```bash
# 修改 docker-compose.yml，移除 postgres 服务
# 或者使用自定义配置
docker-compose up -d foxtrends
```

配置外部数据库：

```bash
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=foxtrends
DB_USER=your_user
DB_PASSWORD=your_password
```

### 选项 4: 开发模式

使用 SQLite 进行本地开发：

```bash
# 修改 .env
DB_DIALECT=sqlite
DB_PATH=/app/foxtrends.db

# 启动（不需要 postgres）
docker-compose up -d foxtrends
```

---

## 管理和维护

### 查看服务状态

```bash
# 查看所有服务
docker-compose ps

# 查看特定服务
docker-compose ps foxtrends
```

### 查看日志

```bash
# 查看所有日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f foxtrends

# 查看最近 100 行日志
docker-compose logs --tail=100 foxtrends
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart foxtrends
```

### 停止服务

```bash
# 停止所有服务
docker-compose stop

# 停止特定服务
docker-compose stop foxtrends
```

### 完全清理

```bash
# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷（警告：会删除所有数据）
docker-compose down -v

# 停止并删除容器、数据卷和镜像
docker-compose down -v --rmi all
```

### 更新应用

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d
```

### 备份数据

#### 备份 PostgreSQL 数据库

```bash
# 导出数据库
docker-compose exec postgres pg_dump -U foxtrends_user foxtrends > backup_$(date +%Y%m%d).sql

# 或使用 docker exec
docker exec foxtrends-postgres pg_dump -U foxtrends_user foxtrends > backup_$(date +%Y%m%d).sql
```

#### 恢复数据库

```bash
# 恢复数据库
docker-compose exec -T postgres psql -U foxtrends_user foxtrends < backup_20240101.sql

# 或使用 docker exec
cat backup_20240101.sql | docker exec -i foxtrends-postgres psql -U foxtrends_user foxtrends
```

#### 备份日志和报告

```bash
# 备份日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# 备份报告
tar -czf reports_backup_$(date +%Y%m%d).tar.gz final_reports/
```

### 监控资源使用

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats foxtrends-app

# 查看磁盘使用
docker system df

# 查看数据卷使用
docker volume ls
```

---

## 高级配置

### 自定义端口

修改 `docker-compose.yml` 中的端口映射：

```yaml
services:
  foxtrends:
    ports:
      - "8080:5000"  # 将 5000 改为 8080
```

### 使用 Nginx 反向代理

创建 `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持
    location /socket.io {
        proxy_pass http://localhost:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 配置 HTTPS

使用 Let's Encrypt 和 Certbot：

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 扩展服务

#### 添加多个 Worker

修改 `docker-compose.yml`:

```yaml
services:
  foxtrends-worker-1:
    <<: *foxtrends-service
    container_name: foxtrends-worker-1
    ports:
      - "5001:5000"

  foxtrends-worker-2:
    <<: *foxtrends-service
    container_name: foxtrends-worker-2
    ports:
      - "5002:5000"
```

#### 使用负载均衡

使用 Nginx 进行负载均衡：

```nginx
upstream foxtrends_backend {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    listen 80;
    location / {
        proxy_pass http://foxtrends_backend;
    }
}
```

---

## 故障排查

### 问题 1: 容器无法启动

**症状**: `docker-compose up` 失败

**解决方案**:

```bash
# 查看详细日志
docker-compose logs

# 检查配置
docker-compose config

# 验证 .env 文件
cat .env

# 重新构建
docker-compose build --no-cache
```

### 问题 2: 数据库连接失败

**症状**: 应用日志显示 "Database connection failed"

**解决方案**:

```bash
# 检查数据库容器状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 测试数据库连接
docker-compose exec postgres psql -U foxtrends_user -d foxtrends

# 重启数据库
docker-compose restart postgres
```

### 问题 3: 端口冲突

**症状**: "port is already allocated"

**解决方案**:

```bash
# 查看端口占用
sudo lsof -i :5000

# 修改端口映射
# 编辑 docker-compose.yml，将 5000 改为其他端口

# 或停止占用端口的服务
sudo kill -9 <PID>
```

### 问题 4: 内存不足

**症状**: 容器频繁重启或 OOM

**解决方案**:

```bash
# 限制容器内存
# 在 docker-compose.yml 中添加：
services:
  foxtrends:
    mem_limit: 2g
    mem_reservation: 1g

# 增加系统 swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 问题 5: 数据丢失

**症状**: 重启后数据消失

**解决方案**:

```bash
# 检查数据卷
docker volume ls

# 检查数据卷挂载
docker-compose config | grep volumes

# 确保使用命名卷而非匿名卷
# 在 docker-compose.yml 中：
volumes:
  postgres_data:
    driver: local
```

### 问题 6: 性能问题

**症状**: 应用响应慢

**解决方案**:

```bash
# 查看资源使用
docker stats

# 增加资源限制
# 在 docker-compose.yml 中：
services:
  foxtrends:
    cpus: '2.0'
    mem_limit: 4g

# 启用 Redis 缓存
docker-compose --profile with-redis up -d

# 优化数据库
docker-compose exec postgres psql -U foxtrends_user -d foxtrends -c "VACUUM ANALYZE;"
```

---

## 生产环境最佳实践

### 1. 安全配置

```bash
# 使用强密码
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)

# 限制网络访问
# 在 docker-compose.yml 中：
services:
  postgres:
    ports: []  # 不暴露端口到主机
```

### 2. 日志管理

```bash
# 配置日志轮转
# 在 docker-compose.yml 中：
services:
  foxtrends:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 健康检查

```bash
# 已在 Dockerfile 中配置
# 可以通过以下命令查看健康状态
docker-compose ps
```

### 4. 自动重启

```bash
# 在 docker-compose.yml 中：
services:
  foxtrends:
    restart: unless-stopped
```

### 5. 监控和告警

使用 Prometheus 和 Grafana：

```yaml
# 添加到 docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

---

## 常用命令速查

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps

# 进入容器
docker-compose exec foxtrends bash

# 更新服务
docker-compose pull && docker-compose up -d

# 清理资源
docker-compose down -v

# 备份数据库
docker-compose exec postgres pg_dump -U foxtrends_user foxtrends > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T postgres psql -U foxtrends_user foxtrends
```

---

## 更多资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [PostgreSQL Docker 镜像](https://hub.docker.com/_/postgres)
- [FoxTrends 项目文档](../README.md)

---

**最后更新**: 2024-11-23

**需要帮助？** 请访问 [GitHub Issues](https://github.com/your-repo/FoxTrends/issues)
