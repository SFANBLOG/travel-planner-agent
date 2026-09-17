"""初始化数据库并注入知识库（手动执行：python -m scripts.init_db）"""
import os
import sys

# 允许以脚本方式运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, SessionLocal
from app.models.user import User
from app.core.security import hash_password
from app.knowledge_base.seed import seed_all


def main():
    init_db()
    print("[init_db] 表已创建")
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", email="admin@travelai.com",
                       password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "admin123456"))))
            db.commit()
            print("[init_db] 已创建默认管理员 admin / admin123456")
        seed_all(db)
        print("[init_db] 知识库注入完成")
    finally:
        db.close()


if __name__ == "__main__":
    main()
