#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preply词汇量测试脚本启动入口

使用方法:
    python run_preply_test.py                # 运行词汇量测试
    python run_preply_test.py --headless     # 无头模式运行
    python run_preply_test.py --help         # 显示帮助信息
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.preply_vocab_test import VocabTestScraper, logger


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description="Preply词汇量测试脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
功能说明:
  在 https://preply.com/en/learn/english/test-your-vocab 网站
  进行词汇量测试，通过两轮点击认识的单词来评估词汇量
  
  ⚠️  注意事项:
  - 目标网站使用Cloudflare人机验证
  - 脚本会自动检测验证页面并等待用户手动完成验证
  - 建议使用有界面模式以便完成人机验证

示例:
  python run_preply_test.py                # 有界面模式运行（推荐）
  python run_preply_test.py --headless     # 无头模式运行（可能无法通过验证）
  python run_preply_test.py --timeout 60   # 设置60秒超时
  python run_preply_test.py --verify-timeout 600  # 设置验证等待时间为10分钟
        """
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="使用无头模式运行浏览器（不显示浏览器窗口）"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="页面加载超时时间（秒），默认30秒"
    )
    
    parser.add_argument(
        "--verify-timeout",
        type=int,
        default=300,
        help="Cloudflare验证等待超时时间（秒），默认300秒（5分钟）"
    )
    
    return parser.parse_args()


def execute_vocab_test(test):
    """
    执行Preply词汇量测试
    
    Args:
        test: PreplyVocabTest实例
    """
    print("\n🎯 开始Preply词汇量测试...")
    print("目标网站: https://preply.com/en/learn/english/test-your-vocab")
    print("测试说明: 通过两轮点击认识的单词来评估您的词汇量")
    print("-" * 60)
    
    # 询问用户第一轮认识的词汇数量
    while True:
        try:
            round1_input = input("\n请输入第一轮您认识的词汇数量 (默认5个): ").strip()
            round1_clicks = int(round1_input) if round1_input else 5
            if round1_clicks > 0:
                break
            else:
                print("请输入大于0的数字")
        except ValueError:
            print("输入无效，请输入数字")
    
    # 询问用户第二轮认识的词汇数量
    while True:
        try:
            round2_input = input("\n请输入第二轮您认识的词汇数量 (默认5个): ").strip()
            round2_clicks = int(round2_input) if round2_input else 5
            if round2_clicks > 0:
                break
            else:
                print("请输入大于0的数字")
        except ValueError:
            print("输入无效，请输入数字")
    
    print(f"\n📚 开始词汇量测试，第一轮将点击 {round1_clicks} 个认识的词汇，第二轮将点击 {round2_clicks} 个认识的词汇...")
    print("💡 测试流程: 第一轮测试完成后等待3秒进入第二轮，第二轮完成后等待5秒获取最终词汇量评估")
    
    result = test.random_click_vocab_labels(round1_clicks, round2_clicks)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 词汇量测试结果")
    print("=" * 60)
    
    if result and result.get('rounds'):
        summary = result['summary']
        print(f"✅ 完成了 {summary['total_rounds']} 轮测试，共 {summary['total_words']} 个单词，您认识 {summary['total_clicked']} 个")
        
        # 显示最终词汇量（如果有）
        if 'final_vocab_size' in result:
            print(f"\n🎯 您的词汇量评估结果: {result['final_vocab_size']} 个单词")
        
        # 按轮次显示详细结果
        for round_data in result['rounds']:
            round_num = round_data['round']
            clicked_count = round_data['clicked_count']
            total_count = round_data['total_count']
            
            print(f"\n📍 第 {round_num} 轮测试: 认识 {clicked_count}/{total_count} 个单词")
            
            # 显示已知单词（被点击的）
            known_words = [word for word in round_data['words'] if word['known']]
            if known_words:
                print(f"   ✅ 认识的单词 ({len(known_words)} 个): {', '.join([w['word'] for w in known_words[:10]])}{'...' if len(known_words) > 10 else ''}")
            
            # 显示未知单词（未被点击的）
            unknown_words = [word for word in round_data['words'] if not word['known']]
            if unknown_words:
                print(f"   ❓ 不认识的单词 ({len(unknown_words)} 个): {', '.join([w['word'] for w in unknown_words[:10]])}{'...' if len(unknown_words) > 10 else ''}")
        
        # 更新日志信息
        if 'final_vocab_size' in result:
            logger.info(f"词汇量测试完成，共执行 {summary['total_rounds']} 轮，认识 {summary['total_clicked']} 个单词，最终词汇量: {result['final_vocab_size']}")
        else:
            logger.info(f"词汇量测试完成，共执行 {summary['total_rounds']} 轮，认识 {summary['total_clicked']} 个单词")
    else:
        print("❌ 词汇量测试未能完成")
        print("\n可能的原因:")
        print("   - 页面中没有找到词汇测试容器")
        print("   - 容器中没有可测试的词汇元素")
        print("   - 网络连接问题或页面加载不完整")
        print("   - Continue按钮点击失败导致测试中断")
        logger.warning("词汇量测试未能完成")
        
    print("\n" + "=" * 60)
    logger.info("词汇量测试任务完成")
    return result


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()
    
    logger.info("=" * 60)
    logger.info("Preply词汇量测试脚本启动")
    logger.info(f"无头模式: {'是' if args.headless else '否'}")
    logger.info(f"页面加载超时: {args.timeout}秒")
    logger.info(f"验证等待超时: {args.verify_timeout}秒")
    logger.info("=" * 60)
    
    # 显示欢迎信息
    print("\n" + "=" * 60)
    print("🚀 Preply词汇量测试工具")
    print("=" * 60)
    print("📚 测试说明:")
    print("   - 通过两轮词汇识别测试评估您的英语词汇量")
    print("   - 每轮测试中点击您认识的单词")
    print("   - 系统将根据您的选择计算最终词汇量")
    print("\n🔧 使用说明:")
    print("   - 预设Cookie自动绕过Cloudflare验证")
    print("   - 如Cookie失效，可能需要手动完成验证")
    if not args.headless:
        print("   - 💡 提示: 如遇到Cloudflare验证，请在浏览器中手动完成验证")
    print("=" * 60)
    
    try:
        # 创建测试实例
        test = VocabTestScraper(
            headless=args.headless,
            timeout=args.timeout,
            verify_timeout=args.verify_timeout
        )
        
        # 直接启动词汇量测试
        execute_vocab_test(test)
        
        print("\n🎉 词汇量测试完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了程序执行")
        logger.info("用户中断程序")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {e}")
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)
    
    finally:
        # 确保WebDriver被正确关闭
        try:
            if 'test' in locals() and test.driver:
                test.driver.quit()
                logger.info("WebDriver 已关闭")
        except:
            pass


if __name__ == "__main__":
    main()