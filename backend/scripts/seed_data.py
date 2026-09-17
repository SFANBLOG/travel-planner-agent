"""仅注入种子数据（跳过建表，需先运行 init_db）：python -m scripts.seed_data"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.knowledge_base.seed import seed_all


def main():
    db = SessionLocal()
    try:
        seed_all(db)
        print("[seed_data] 完成")
    finally:
        db.close()


if __name__ == "__main__":
    main()
