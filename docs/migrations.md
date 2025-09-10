# 数据库迁移指南

本文档介绍了如何使用 Alembic 进行数据库迁移管理。

## 快速开始

### 1. 运行迁移

```bash
# 使用 dev.sh 脚本
./dev.sh migrate

# 使用 Python 脚本
python migrate.py up

# 直接使用 Alembic
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic upgrade head
```

### 2. 创建新的迁移

```bash
# 使用 dev.sh 脚本（推荐）
./dev.sh migration-create "add_new_feature"

# 使用 Python 脚本
python migrate.py create "add_new_feature"

# 直接使用 Alembic
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic revision --autogenerate -m "add_new_feature"
```

### 3. 回滚迁移

```bash
# 回滚上一个迁移
./dev.sh migrate-down
python migrate.py down

# 回滚到指定版本
python migrate.py down base
```

## 可用命令

### 使用 dev.sh 脚本

```bash
# 运行所有迁移
./dev.sh migrate

# 创建新迁移
./dev.sh migration-create "migration_name"

# 回滚迁移
./dev.sh migrate-down

# 查看迁移历史
./dev.sh migrate-history

# 查看当前状态
./dev.sh migrate-current
```

### 使用 Python 脚本

```bash
# 运行迁移
python migrate.py up

# 创建迁移（自动生成）
python migrate.py create "migration_name"

# 创建迁移（手动）
python migrate.py create-manual "migration_name"

# 回滚迁移
python migrate.py down [revision]

# 查看历史
python migrate.py history

# 查看当前状态
python migrate.py current

# 查看详细状态
python migrate.py show

# 标记版本
python migrate.py stamp [revision]
```

### 直接使用 Alembic

```bash
# 运行迁移
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic upgrade head

# 创建迁移
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic revision --autogenerate -m "migration_name"

# 回滚迁移
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic downgrade -1

# 查看历史
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic history

# 查看当前状态
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic current
```

## 迁移文件结构

迁移文件位于 `alembic/versions/` 目录下：

```
alembic/
├── versions/
│   ├── 2a21da56f8bc_initial_migration.py    # 初始迁移
│   └── 9bed4a0ddb63_add_seed_data.py        # 测试数据
├── env.py                                   # 迁移环境配置
├── script.py.mako                           # 迁移模板
└── README                                   # Alembic 说明
```

## 迁移最佳实践

### 1. 命名约定

- 使用描述性的名称，如 `add_user_table`、`create_post_index`
- 使用下划线分隔单词，如 `add_email_confirmation_to_users`
- 使用动词开头描述操作，如 `create`、`add`、`remove`、`update`

### 2. 迁移内容

- **Schema 变更**: 表的创建、修改、删除
- **数据变更**: 批量更新数据、添加默认值
- **索引优化**: 添加或删除索引
- **约束变更**: 添加外键、唯一约束等

### 3. 数据安全

- 在生产环境运行迁移前先备份数据
- 测试迁移的 downgrade 操作
- 避免在迁移中删除重要数据

### 4. 迁移顺序

- 先运行所有迁移到开发环境
- 在测试环境验证迁移
- 最后在生产环境运行

## 测试数据

项目包含以下测试数据：

### 用户数据
- **管理员**: admin@example.com / Admin123!
- **普通用户**: user1@example.com / User123!
- **普通用户**: user2@example.com / User123!
- **作者**: author@example.com / Author123!

### 标签数据
- Python (#3776ab)
- FastAPI (#009688)
- 数据库 (#ff5722)
- 前端 (#2196f3)
- DevOps (#4caf50)

### 文章数据
- FastAPI 入门教程
- Python 数据库编程
- Docker 容器化部署指南
- 前端开发最佳实践

## 故障排除

### 1. 数据库连接问题

确保 PostgreSQL 服务正在运行：

```bash
# 检查服务状态
docker compose ps postgres

# 启动服务
docker compose up -d postgres
```

### 2. 迁移冲突

如果遇到迁移冲突，可以：

```bash
# 查看当前状态
./dev.sh migrate-current

# 回滚到冲突前的版本
python migrate.py down <conflict_revision>

# 手动解决冲突后重新运行
./dev.sh migrate
```

### 3. 权限问题

确保数据库用户有足够的权限：

```sql
GRANT ALL PRIVILEGES ON DATABASE fastapi_starter TO user;
GRANT ALL ON SCHEMA public TO user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO user;
```

## 环境变量

确保设置了正确的数据库 URL：

```bash
# 开发环境
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter

# 测试环境
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter_test

# 生产环境
DATABASE_URL=postgresql+asyncpg://user:password@prod-db.example.com:5432/fastapi_starter
```

## 自动化集成

可以将迁移集成到 CI/CD 流程中：

```yaml
# GitHub Actions 示例
- name: Run database migrations
  run: |
    python migrate.py up
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## 总结

使用 Alembic 进行数据库迁移提供了以下优势：

- **版本控制**: 数据库 schema 变更的版本控制
- **自动化**: 自动生成迁移文件
- **回滚能力**: 支持迁移的回滚
- **团队协作**: 多人开发时的数据库同步
- **生产安全**: 在生产环境安全地应用变更

遵循本文档的最佳实践，可以确保数据库迁移的安全性和可靠性。