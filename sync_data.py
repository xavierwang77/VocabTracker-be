#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词汇数据同步脚本启动入口

使用方法:
    python sync_data.py                    # 同步所有数据文件
    python sync_data.py --file cet4.json  # 同步指定文件
    python sync_data.py --help            # 显示帮助信息
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.sync_vocabulary import VocabularyDataSync, logger
from app.db import check_db_connection, init_db


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description="词汇数据同步脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的数据文件:
  cet4.json    - CET4词汇数据
  cet6.json    - CET6词汇数据
  kaoyan.json  - 考研词汇数据
  level4.json  - 专四词汇数据
  level8.json  - 专八词汇数据

示例:
  python sync_data.py                    # 同步所有文件
  python sync_data.py --file cet4.json  # 只同步CET4数据
  python sync_data.py --datasets-dir ./data  # 指定数据目录
        """
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="指定要同步的单个文件名（如: cet4.json）"
    )
    
    parser.add_argument(
        "--datasets-dir",
        type=str,
        default="datasets",
        help="数据集目录路径（默认: datasets）"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制同步，即使数据库中已有数据"
    )
    
    return parser.parse_args()


def validate_environment():
    """
    验证运行环境
    """
    logger.info("检查运行环境...")
    
    # 检查数据库连接
    if not check_db_connection():
        logger.error("数据库连接失败，请检查以下配置:")
        logger.error("- 数据库服务是否启动")
        logger.error("- 连接参数是否正确 (localhost:5969)")
        logger.error("- 用户名密码是否正确 (postgres/xwCoder4Ever!)")
        logger.error("- 数据库 'vocabtracker' 是否存在")
        return False
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False
    
    return True


def main():
    """
    主函数
    """
    print("\n" + "="*60)
    print("           词汇数据同步脚本")
    print("="*60)
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 验证环境
    if not validate_environment():
        logger.error("环境验证失败，程序退出")
        sys.exit(1)
    
    # 检查数据集目录
    datasets_dir = Path(args.datasets_dir)
    if not datasets_dir.exists():
        logger.error(f"数据集目录不存在: {datasets_dir}")
        logger.info("请确保数据集目录存在并包含以下文件:")
        logger.info("- cet4.json")
        logger.info("- cet6.json")
        logger.info("- kaoyan.json")
        logger.info("- level4.json")
        logger.info("- level8.json")
        sys.exit(1)
    
    # 执行数据同步
    try:
        with VocabularyDataSync(datasets_dir=str(datasets_dir)) as sync_tool:
            if args.file:
                # 同步指定文件
                logger.info(f"开始同步指定文件: {args.file}")
                if sync_tool.sync_file(args.file):
                    logger.info(f"✅ 文件 {args.file} 同步成功")
                else:
                    logger.error(f"❌ 文件 {args.file} 同步失败")
                    sys.exit(1)
            else:
                # 同步所有文件
                logger.info("开始同步所有词汇数据文件...")
                if sync_tool.sync_all():
                    logger.info("✅ 所有数据同步成功")
                else:
                    logger.error("❌ 部分数据同步失败")
                    sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"同步过程中发生未预期的错误: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("           数据同步完成")
    print("="*60)
    logger.info("可以使用以下命令启动API服务:")
    logger.info("python run.py")


if __name__ == "__main__":
    main()