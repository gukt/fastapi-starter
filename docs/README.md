# 项目文档

本文档包含了 FastAPI 项目的详细说明和最佳实践。

## 文档结构

### 📁 核心文档

- **[项目结构最佳实践](./project-structure-best-practices.md)**
  - 领域驱动设计（DDD）架构
  - 各层职责说明
  - 代码组织原则
  - 常见陷阱和解决方案

- **[领域模块开发指南](./domain-module-development-guide.md)**
  - 创建新领域模块的详细步骤
  - 完整的代码示例
  - 最佳实践和常见问题
  - 测试指南

### 🏗️ 架构设计

本项目采用 **领域驱动设计（DDD）** 的简化架构，结合了 FastAPI 的最佳实践。

#### 核心特点

- **领域驱动**：每个业务领域独立管理自己的模型、服务和 API
- **简化结构**：避免过度工程化，每个领域模块只包含必要的核心文件
- **清晰职责**：模型层、服务层、路由层、依赖层各司其职
- **类型安全**：100% 类型注解覆盖

#### 项目结构

```
app/
├── auth/              # 认证领域模块
│   ├── models.py      # 用户模型 (SQLAlchemy)
│   ├── schemas.py     # Pydantic 数据模式
│   ├── service.py     # 业务逻辑层
│   ├── router.py      # API 路由层
│   ├── dependencies.py # 依赖注入
│   ├── constants.py   # 常量定义
│   └── exceptions.py  # 自定义异常
├── posts/             # 文章领域模块
│   ├── models.py      # 文章、标签模型
│   ├── schemas.py     # Pydantic 数据模式
│   ├── service.py     # 业务逻辑层
│   ├── router.py      # API 路由层
│   ├── dependencies.py # 依赖注入
│   ├── constants.py   # 常量定义
│   └── exceptions.py  # 自定义异常
├── core/              # 核心基础设施
├── database/          # 数据库层
├── utils/             # 工具模块
└── main.py            # FastAPI 应用入口
```

### 🚀 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd fastapi-starter
   ```

2. **安装依赖**
   ```bash
   ./dev.sh setup
   ```

3. **启动服务**
   ```bash
   ./dev.sh dev
   ```

4. **访问文档**
   - Swagger UI: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc

### 📚 学习资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [领域驱动设计](https://domainlanguage.com/ddd/)

### 🤝 贡献指南

1. 阅读 [项目结构最佳实践](./project-structure-best-practices.md)
2. 查看 [领域模块开发指南](./domain-module-development-guide.md)
3. 遵循既定的代码规范和架构模式
4. 为新功能编写相应的测试

### 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件
- 参与讨论

---

*最后更新：2024-01-01*