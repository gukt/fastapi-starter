#!/usr/bin/env python3
"""
数据库迁移管理脚本
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


def get_database_url():
    """获取数据库 URL"""
    return settings.database_url


def run_alembic_command(command, description=None):
    """运行 Alembic 命令"""
    if description:
        print(f"\033[1;34m[INFO]\033[0m {description}")
    
    env = os.environ.copy()
    env['DATABASE_URL'] = get_database_url()
    
    try:
        result = subprocess.run(
            ['alembic'] + command,
            env=env,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31m[ERROR]\033[0m Command failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def migrate_up():
    """运行迁移到最新版本"""
    return run_alembic_command(['upgrade', 'head'], "Running database migrations...")


def migrate_down(revision='-1'):
    """回滚迁移"""
    return run_alembic_command(['downgrade', revision], f"Rolling back to revision {revision}...")


def migrate_create(name, autogenerate=True):
    """创建新的迁移文件"""
    if not name:
        print("\033[1;31m[ERROR]\033[0m Migration name is required")
        return False
    
    cmd = ['revision', '-m', name]
    if autogenerate:
        cmd.append('--autogenerate')
    
    return run_alembic_command(cmd, f"Creating migration: {name}")


def migrate_history():
    """显示迁移历史"""
    return run_alembic_command(['history', '--verbose'], "Showing migration history...")


def migrate_current():
    """显示当前迁移状态"""
    return run_alembic_command(['current'], "Showing current migration...")


def migrate_show():
    """显示迁移状态"""
    return run_alembic_command(['show'], "Showing migration status...")


def migrate_init():
    """初始化迁移环境"""
    return run_alembic_command(['init', 'alembic'], "Initializing migration environment...")


def migrate_stamp(revision='head'):
    """标记数据库版本"""
    return run_alembic_command(['stamp', revision], f"Stamping database to revision {revision}...")


def show_help():
    """显示帮助信息"""
    print("""
Database Migration Management Script

Usage: python migrate.py [command] [options]

Commands:
  up                    Run migrations to latest version
  down [revision]       Rollback migrations (default: -1)
  create <name>         Create new migration with autogenerate
  create-manual <name>  Create new migration without autogenerate
  history               Show migration history
  current               Show current migration status
  show                  Show migration status
  init                  Initialize migration environment
  stamp [revision]      Stamp database to revision (default: head)
  help                  Show this help message

Examples:
  python migrate.py up
  python migrate.py down
  python migrate.py create "add_user_table"
  python migrate.py create-manual "custom_migration"
  python migrate.py stamp head
""")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == 'up':
        migrate_up()
    elif command == 'down':
        revision = sys.argv[2] if len(sys.argv) > 2 else '-1'
        migrate_down(revision)
    elif command == 'create':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        migrate_create(name)
    elif command == 'create-manual':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        migrate_create(name, autogenerate=False)
    elif command == 'history':
        migrate_history()
    elif command == 'current':
        migrate_current()
    elif command == 'show':
        migrate_show()
    elif command == 'init':
        migrate_init()
    elif command == 'stamp':
        revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
        migrate_stamp(revision)
    elif command == 'help':
        show_help()
    else:
        print(f"\033[1;31m[ERROR]\033[0m Unknown command: {command}")
        show_help()


if __name__ == '__main__':
    main()