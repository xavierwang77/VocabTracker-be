#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词汇测试网站数据抓取脚本

使用Selenium从Preply网站抓取词汇测试相关数据
用于结果比对和数据验证
"""

import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VocabTestScraper:
    """
    词汇测试网站数据抓取器
    用于从Preply网站抓取词汇测试相关数据
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30, verify_timeout: int = 300):
        """
        初始化抓取器
        
        Args:
            headless: 是否使用无头模式运行浏览器
            timeout: 页面加载超时时间（秒）
            verify_timeout: Cloudflare验证等待超时时间（秒）
        """
        self.headless = headless
        self.timeout = timeout
        self.verify_timeout = verify_timeout
        self.driver = None
        self.target_url = "https://preply.com/en/learn/english/test-your-vocab"

        self.cookies_original = {
            'init_uid': '9f168d9385908ebc06d735e442b45b54dbd185a372b17a71ac34bad70b01c71d',
            'uid': '9f168d9385908ebc06d735e442b45b54dbd185a372b17a71ac34bad70b01c71d',
            'sessionid': 'ld7etf6943robyrx7lzj6qqothc4yj6g',
            'm_source': 'preply',
            'm_source_landing': '/en/learn/english/test-your-vocab',
            'm_source_details': '',
            'is_source_set': 'yes',
            'source_page': 'https://preply.com/en/learn/english/test-your-vocab?__cf_chl_tk=fmXqIWZzL5kpv9SElDkkiVaVueCIv505xp4np5eZkvo-1750733984-1.0.1.1-ZYOumU0vn.yLNimM2FveGYi5e5Rb7DkVDi6sQCCZuNU',
            'landing_page': 'https://preply.com/en/learn/english/test-your-vocab',
            'visit_time': '2025-06-24T02:59:55.841Z',
            'browserTimezone': 'Asia/Shanghai',
            'csrftoken': '6jkSqedrALcA3h5M2PDOKx2u01Y4fTVm',
            '_tt_enable_cookie': '1',
            '_ttp': '01JYFY1KK8H2J5H0R80GK6YFX6_.tt.1',
            '_gcl_au': '1.1.773175677.1750734002',
            '_ga': 'GA1.1.301526963.1750734002',
            'hj_first_visit_30days': '2025-06-24T03:00:01.832Z',
            'eu_cookie_policy': 'yes',
            '_hjSession_641144': 'eyJpZCI6IjAxZWZkNWVhLTg1MzMtNDg0ZC05OGVjLWZiMzNmOTkyZDFkYyIsImMiOjE3NTA3MzQwMDU1NzcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=',
            '_clck': '7s8otm%7C2%7Cfx1%7C0%7C2001',
            'hubspotutk': '3d687f7dedec35188d1a23bf24f47423',
            '_fbp': 'fb.1.1750734007977.971242542358675962',
            '_hjSessionUser_641144': 'eyJpZCI6IjU1NTljOTcyLTQxYjQtNTYyZC1iMmUxLWE3NGFmZDc2OTRhOSIsImNyZWF0ZWQiOjE3NTA3MzQwMDU1NzcsImV4aXN0aW5nIjp0cnVlfQ==',
            'currency_code': 'AUD',
            '_hjHasCachedUserAttributes': 'true',
            '__hssrc': '1',
            'source_page_last': '',
            'landing_page_last': 'https://preply.com/en/learn/english/test-your-vocab',
            '__hstc': '115815577.3d687f7dedec35188d1a23bf24f47423.1750734007345.1750740533417.1750745780803.4',
            '__hssc': '115815577.5.1750745780803',
            'visit_time_last': '2025-06-24T06:22:01.155Z',
            'pv_count': '27',
            '_ga_BQH4D3BLSB': 'GS2.1.s1750745760$o3$g1$t1750746121$j50$l0$h0',
            '_uetsid': '53f63bb050a711f095bf27f3078b7844',
            '_uetvid': '53f676d050a711f0ad38032b5eaa9584',
            'ttcsid': '1750745775924::uQTIt5svN5eow7qJEvOP.3.1750746122318',
            'ttcsid_C525UPO00UN7QUNERGG0': '1750745775924::YGK_ql7mG8ZQGjnum7Q-.2.1750746122529',
            '_clsk': '1pz4jg3%7C1750746123623%7C6%7C0%7Cl.clarity.ms%2Fcollect',
            '__cf_bm': '9._QgCYfEG994klcHlPsvHCfDSxxW.nm7CLQ8H5AWOg-1750746140-1.0.1.1-eCPsIPzHd2DanQatUAISdo0zQoQ_2UU3cH_V4dN9d4xr8EDRsBWZl342io8xLwdtqjoSPrNAp0WWaqbCkr6FRAwZJYMsKJvr0jOstIcYQ2Y',
            '_cfuvid': 'MwpC2rE6JO34VaGvLz9_bTRZgzAPZQ6Pb5eKMfhvlho-1750746140314-0.0.1.1-604800000',
            'cf_clearance': 'YVh9QGXibIRVAvm9MHrs56nqtwOtlOEkZ4d2cGYwWWE-1750746147-1.2.1.1-Rm7rSWY.ywiIZQy_UQPNeMN.0F4yjsfVeZr8WwyE9VqTKgl_xY_iv2S_aCw.oqO58azfmkwWdHTgRRRBdtFc6iwl2nt0xxGLiTaEp6kmazVetAoXUNE4qANzQIlcFHpE1vZRjwpR8uECOLyopIkb_xYrbiFyGuD9.dSxzJ2VxITpoenWqyNBGOMkuvxB1rcGuqN0w67o15zvt9_CZVTzdoriKa1ekFP1wABjs.J7zincInrvrEwZIbCJL1raFRDr_1qw2qh9QdFIf1OxmJmXniy0rJ9w8JMAZcY1iw6Hatp5tNpnGhsiHwcYtVEB3xl81DkAIWZFvDfokNimNLaN29KsSGA5x2Ax8VIniRuXWtIFsFgVO4EomBJTfNRuCSEW',
        }

        
        # 预设的Cookie数据（用于绕过Cloudflare验证）
        self.cookies = []
        
        # 目标div的class属性
        self.target_class = (
            "LayoutGap__FdLKD LayoutHide__Q53jS LayoutRelative__PQtO7 "
            "LayoutPadding__MyMdq LayoutPadding--padding-top-24__-kirr "
            "LayoutPadding--padding-right-24__a8DuH LayoutPadding--padding-bottom-24__aTb-7 "
            "LayoutPadding--padding-left-24__d5III LayoutPadding--medium-s--padding-top-48__oIdZF "
            "LayoutPadding--medium-s--padding-right-96__CR5VM "
            "LayoutPadding--medium-s--padding-bottom-48__inapi "
            "LayoutPadding--medium-s--padding-left-96__-g76x"
        )
        
        # 词汇测试容器的class属性
        self.vocab_test_container_class = (
            "LayoutGrid__-dslt LayoutGap__FdLKD LayoutGap--gap-24__naegM "
            "LayoutPadding__MyMdq LayoutPadding--padding-top-none__EDOlv "
            "LayoutPadding--padding-right-none__l2yuQ LayoutPadding--padding-bottom-none__y-IEv "
            "LayoutPadding--padding-left-none__3-vQ1 LayoutHide__Q53jS "
            "LayoutRelative__PQtO7 LayoutGrid--columns__kFwZC"
        )

        # 初始化Selenium所需的cookies
        self.init_cookies_from_original()

    def init_cookies_from_original(self, domain=".preply.com"):
        """
        根据 cookies_original 初始化 Selenium 所需格式的 cookies 列表

        Args:
            domain (str): cookie 所属的域名，默认 ".preply.com"
        """
        self.cookies = []
        for name, value in self.cookies_original.items():
            cookie = {
                "name": name,
                "value": value,
                "domain": domain
            }
            self.cookies.append(cookie)
    
    def _setup_driver(self):
        """
        设置Chrome WebDriver
        """
        try:
            # 配置Chrome选项
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            # 基础选项
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 获取下载目录
            path = ChromeDriverManager().install()

            # 修复路径指向非可执行文件问题
            correct_driver_path = os.path.join(os.path.dirname(path), "chromedriver")
            
            # 自动下载并设置ChromeDriver
            service = Service(executable_path=correct_driver_path)
            
            # 创建WebDriver实例
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            # 隐藏WebDriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 修改其他可能暴露自动化的属性
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
            """)
            
            # 先访问目标域名以设置Cookie
            logger.info("正在访问目标域名以设置Cookie...")
            self.driver.get("https://preply.com")
            time.sleep(2)
            
            # 添加预设的Cookie
            logger.info("正在添加预设Cookie...")
            for cookie in self.cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"添加Cookie失败: {cookie['name']} - {e}")
            
            logger.info("Chrome WebDriver 初始化成功")
            
        except Exception as e:
            logger.error(f"WebDriver 初始化失败: {e}")
            raise
    

    
    def _wait_for_page_load(self):
        """
        等待页面完全加载
        """
        try:
            # 等待页面标题加载
            WebDriverWait(self.driver, self.timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 额外等待一些时间确保动态内容加载
            time.sleep(3)
            
            logger.info("页面加载完成")
            
        except TimeoutException:
            logger.warning("页面加载超时，但继续执行")
    
    def _wait_for_cloudflare_verification(self, max_wait_time: int = 300):
        """
        等待Cloudflare人机验证完成
        
        Args:
            max_wait_time: 最大等待时间（秒），默认5分钟
        """
        logger.info("检测到可能的Cloudflare验证页面")
        
        # 检查是否存在Cloudflare验证元素
        cloudflare_indicators = [
            "//title[contains(text(), 'Just a moment')]",
            "//div[contains(@class, 'cf-browser-verification')]",
            "//div[contains(@class, 'cf-checking-browser')]",
            "//div[contains(text(), 'Checking your browser')]",
            "//div[contains(text(), 'Please wait')]",
            "//div[contains(@class, 'cf-challenge')]",
            "//div[contains(@class, 'cf-wrapper')]",
            "//div[contains(text(), 'Verify you are human')]"
        ]
        
        # 目标页面的特征元素（用于确认已到达目标页面）
        target_page_indicators = [
            "//div[contains(@class, 'LayoutGap__FdLKD')]",
            "//h1[contains(text(), 'Test your vocabulary')]",
            "//div[contains(text(), 'vocabulary test')]",
            "//button[contains(text(), 'Start test')]"
        ]
        
        is_cloudflare_page = False
        for indicator in cloudflare_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, indicator)
                if elements:
                    is_cloudflare_page = True
                    break
            except:
                continue
        
        # 检查是否已经在目标页面
        is_target_page = False
        for indicator in target_page_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, indicator)
                if elements:
                    is_target_page = True
                    break
            except:
                continue
        
        if not is_cloudflare_page and is_target_page:
            logger.info("已在目标页面，无需验证")
            return
        
        if not is_cloudflare_page:
            logger.info("未检测到Cloudflare验证页面，继续执行")
            return
        
        print("\n" + "="*60)
        print("🔒 检测到Cloudflare人机验证页面")
        print("📋 请按照以下步骤操作:")
        print("   1. 在打开的浏览器窗口中完成人机验证")
        print("   2. 等待页面自动跳转到目标内容")
        print("   3. 验证完成后，脚本将自动继续")
        print("\n⚠️  注意: 请不要关闭浏览器窗口!")
        print("="*60)
        
        # 等待用户手动验证
        start_time = time.time()
        verification_completed = False
        last_url = self.driver.current_url
        
        print("\n⏳ 自动检测验证状态中... (每3秒检查一次)")
        print("💡 提示: 如果验证完成但未自动检测到，请按 Ctrl+C 然后手动确认继续")
        
        while time.time() - start_time < max_wait_time and not verification_completed:
            try:
                # 检查是否已经通过验证
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                logger.info(f"当前页面标题: {page_title}")
                logger.info(f"当前URL: {current_url}")
                
                # 检查URL是否发生变化（可能表示重定向完成）
                url_changed = current_url != last_url
                last_url = current_url
                
                # 多重检查验证是否完成
                verification_checks = [
                    # 检查1: 页面标题不包含验证相关内容
                    ("Just a moment" not in page_title and 
                     "Checking" not in page_title and
                     "Please wait" not in page_title and
                     "Verify you are human" not in page_title and
                     current_url != "about:blank"),
                    
                    # 检查2: 目标页面元素存在
                    any(self.driver.find_elements(By.XPATH, indicator) for indicator in target_page_indicators),
                    
                    # 检查3: URL包含目标路径
                    "test-your-vocab" in current_url.lower(),
                    
                    # 检查4: 页面源码包含目标内容
                    "vocabulary test" in self.driver.page_source.lower() or "preply" in self.driver.page_source.lower()
                ]
                
                # 如果多个检查通过，认为验证完成
                passed_checks = sum(verification_checks)
                logger.info(f"验证检查通过数: {passed_checks}/4")
                
                if passed_checks >= 2:  # 至少2个检查通过
                    # 再次确认没有验证元素
                    still_verifying = False
                    for indicator in cloudflare_indicators:
                        try:
                            elements = self.driver.find_elements(By.XPATH, indicator)
                            if elements and any(elem.is_displayed() for elem in elements):
                                still_verifying = True
                                break
                        except:
                            continue
                    
                    if not still_verifying:
                        logger.info("检测到验证已完成，自动继续")
                        print("\n✅ 检测到验证已完成，页面已加载")
                        verification_completed = True
                        break
                    else:
                        logger.info(f"验证检查未完全通过，继续等待...")
                
                # 显示等待状态
                elapsed_time = int(time.time() - start_time)
                remaining_time = max_wait_time - elapsed_time
                print(f"\r⏱️  等待验证完成... 已等待 {elapsed_time}s，剩余 {remaining_time}s (检查通过: {passed_checks}/4)", end="", flush=True)
                
                time.sleep(3)  # 每3秒检查一次，提高响应速度
                
            except KeyboardInterrupt:
                print("\n\n⚠️  检测到用户中断")
                user_choice = input("是否继续执行数据抓取？(y/n): ").strip().lower()
                if user_choice in ['y', 'yes', '是']:
                    print("✅ 用户确认继续执行")
                    verification_completed = True
                    break
                else:
                    logger.info("用户选择退出")
                    raise KeyboardInterrupt("用户手动退出")
            except Exception as e:
                logger.warning(f"验证检查过程中出现异常: {e}")
                time.sleep(3)
        
        if not verification_completed and time.time() - start_time >= max_wait_time:
            print(f"\n⚠️  等待超时 ({max_wait_time}秒)")
            # 最后一次检查是否在目标页面
            try:
                current_url = self.driver.current_url
                if "test-your-vocab" in current_url.lower():
                    print("✅ 检测到已在目标页面，继续执行")
                    verification_completed = True
                else:
                    user_choice = input("是否强制继续执行数据抓取？(y/n): ").strip().lower()
                    if user_choice not in ['y', 'yes', '是']:
                        raise TimeoutException("验证等待超时，用户选择退出")
            except Exception as e:
                logger.warning(f"最终检查时出现异常: {e}")
                user_choice = input("是否强制继续执行数据抓取？(y/n): ").strip().lower()
                if user_choice not in ['y', 'yes', '是']:
                    raise TimeoutException("验证等待超时，用户选择退出")
        
        # 最终等待页面稳定
        logger.info("等待页面稳定...")
        time.sleep(10)  # 减少等待时间
        
        # 验证完成后，确保页面完全加载
        try:
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logger.info("页面加载状态确认完成")
        except TimeoutException:
            logger.warning("页面加载状态检查超时，但继续执行")
        
        print("\n🚀 继续执行数据抓取...")
    
    def random_click_vocab_labels(self, round1_clicks=5, round2_clicks=5):
        """
        随机点击词汇测试容器中的label元素，固定执行两轮点击
        
        Args:
            round1_clicks: 第一轮要点击的label数量，默认为5个
            round2_clicks: 第二轮要点击的label数量，默认为5个
            
        Returns:
            dict: 包含所有轮次单词信息的字典，格式为:
            {
                'rounds': [
                    {
                        'round': 1,
                        'words': [{'word': '单词', 'known': True/False, 'for': 'label_id'}],
                        'clicked_count': 5,
                        'total_count': 20
                    }
                ],
                'summary': {
                    'total_rounds': 2,
                    'total_words': 40,
                    'total_clicked': 10
                },
                'final_vocab_size': '3406'
            }
        """
        result = {
            'rounds': [],
            'summary': {
                'total_rounds': 0,
                'total_words': 0,
                'total_clicked': 0
            }
        }
        
        try:
            # 如果driver未初始化，先初始化
            if not self.driver:
                self._setup_driver()
                logger.info(f"正在访问目标网站: {self.target_url}")
                self.driver.get(self.target_url)
                self._wait_for_page_load()
                self._wait_for_cloudflare_verification(self.verify_timeout)
            
            # 执行固定两轮点击
            rounds = 2
            click_counts = [round1_clicks, round2_clicks]
            
            for round_num in range(rounds):
                current_click_count = click_counts[round_num]
                logger.info(f"开始第 {round_num + 1} 轮点击，本轮点击 {current_click_count} 个label")
                print(f"\n🎯 第 {round_num + 1} 轮点击开始（点击 {current_click_count} 个label）...")
                
                round_result = self._click_labels_in_current_page(current_click_count, round_num + 1)
                
                # 构建轮次结果
                round_data = {
                    'round': round_num + 1,
                    'words': round_result['words'],
                    'clicked_count': len(round_result['clicked_labels']),
                    'total_count': len(round_result['words'])
                }
                result['rounds'].append(round_data)
                
                # 更新汇总信息
                result['summary']['total_words'] += len(round_result['words'])
                result['summary']['total_clicked'] += len(round_result['clicked_labels'])
                
                # 点击Continue按钮并等待（包括最后一轮）
                if self._click_continue_button():
                    if round_num < rounds - 1:
                        logger.info("Continue按钮点击成功，等待3秒加载下一页")
                        print("⏳ 等待3秒加载下一页...")
                        time.sleep(3)
                    else:
                        logger.info("最后一轮Continue按钮点击成功，等待5秒获取最终结果")
                        print("⏳ 等待5秒获取最终词汇量结果...")
                        time.sleep(5)
                        
                        # 捕获最终词汇量
                        final_vocab_size = self._capture_final_vocab_size()
                        if final_vocab_size:
                            result['final_vocab_size'] = final_vocab_size
                            logger.info(f"捕获到最终词汇量: {final_vocab_size}")
                            print(f"🎉 最终词汇量: {final_vocab_size}")
                        else:
                            logger.warning("未能捕获到最终词汇量")
                            print("⚠️ 未能捕获到最终词汇量")
                else:
                    if round_num < rounds - 1:
                        logger.warning("Continue按钮点击失败，停止后续轮次")
                        break
                    else:
                        logger.warning("最后一轮Continue按钮点击失败，无法获取最终词汇量")
            
            # 完成汇总信息
            result['summary']['total_rounds'] = len(result['rounds'])
            
            logger.info(f"所有轮次完成，总共 {result['summary']['total_rounds']} 轮，{result['summary']['total_words']} 个单词，点击了 {result['summary']['total_clicked']} 个")
            
            # 输出JSON格式结果
            import json
            import os
            from datetime import datetime
            
            json_result = json.dumps(result, ensure_ascii=False, indent=2)
            print(f"\n📊 点击结果JSON:")
            print(json_result)
            
            # 保存JSON结果到文件
            try:
                # 创建结果目录（如果不存在）
                results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
                os.makedirs(results_dir, exist_ok=True)
                
                # 生成文件名（包含时间戳）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vocab_test_result_{timestamp}.json"
                filepath = os.path.join(results_dir, filename)
                
                # 保存到文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_result)
                
                logger.info(f"结果已保存到文件: {filepath}")
                print(f"💾 结果已保存到文件: {filepath}")
                
            except Exception as e:
                logger.error(f"保存JSON文件时发生错误: {e}")
                print(f"⚠️ 保存JSON文件失败: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"随机点击label过程中发生错误: {e}")
            return result
    
    def _click_labels_in_current_page(self, click_count, round_num):
        """
        在当前页面中点击指定数量的label元素，并收集所有单词信息
        
        Args:
            click_count: 要点击的label数量
            round_num: 当前轮次编号
            
        Returns:
            dict: 包含所有单词信息的字典，格式为 {'words': [{'word': str, 'known': bool, 'for': str}], 'clicked_labels': []}
        """
        result = {
            'words': [],
            'clicked_labels': []
        }
        
        try:
            logger.info(f"正在查找词汇测试容器，class: {self.vocab_test_container_class}")
            
            # 查找词汇测试容器
            container_elements = self.driver.find_elements(
                By.XPATH, 
                f"//div[@class='{self.vocab_test_container_class}']"
            )
            
            if not container_elements:
                # 如果完整匹配失败，尝试部分匹配
                logger.info("完整class匹配失败，尝试部分匹配...")
                container_elements = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'LayoutGrid__-dslt') and contains(@class, 'LayoutGrid--columns__kFwZC')]"
                )
            
            if not container_elements:
                logger.warning(f"第 {round_num} 轮：未找到词汇测试容器")
                return result
            
            logger.info(f"第 {round_num} 轮：找到 {len(container_elements)} 个词汇测试容器")
            
            # 在每个容器中查找label元素
            all_labels = []
            for container in container_elements:
                try:
                    # 查找容器内所有含有for="word_xxx"属性的label元素
                    labels = container.find_elements(
                        By.XPATH,
                        ".//label[starts-with(@for, 'word_')]"
                    )
                    all_labels.extend(labels)
                    logger.info(f"第 {round_num} 轮：在容器中找到 {len(labels)} 个label元素")
                except Exception as e:
                    logger.warning(f"第 {round_num} 轮：在容器中查找label元素时出错: {e}")
            
            if not all_labels:
                logger.warning(f"第 {round_num} 轮：未找到任何含有for='word_xxx'属性的label元素")
                return result
            
            logger.info(f"第 {round_num} 轮：总共找到 {len(all_labels)} 个可点击的label元素")
            
            # 收集所有label内第一个span标签的文本作为单词
            all_words_info = []
            for label in all_labels:
                try:
                    label_for = label.get_attribute('for')
                    # 查找label内的第一个span标签
                    span_elements = label.find_elements(By.XPATH, ".//span")
                    if span_elements:
                        word_text = span_elements[0].text.strip()
                        if word_text:  # 只保存非空的单词
                            word_info = {
                                'word': word_text,
                                'known': False,  # 默认为未知
                                'for': label_for,
                                'label_element': label  # 临时保存元素引用用于点击
                            }
                            all_words_info.append(word_info)
                            logger.debug(f"第 {round_num} 轮：收集到单词: {word_text} (for={label_for})")
                except Exception as e:
                    logger.warning(f"第 {round_num} 轮：收集label单词时出错: {e}")
            
            logger.info(f"第 {round_num} 轮：收集到 {len(all_words_info)} 个单词")
            
            # 随机选择要点击的label
            click_count = min(click_count, len(all_words_info))
            selected_words = random.sample(all_words_info, click_count)
            
            logger.info(f"第 {round_num} 轮：随机选择了 {click_count} 个单词进行点击")
            
            # 创建点击的单词for属性集合，用于快速查找
            clicked_for_set = {word['for'] for word in selected_words}
            
            # 点击选中的单词对应的label
            for i, word_info in enumerate(selected_words):
                try:
                    label = word_info['label_element']
                    word_text = word_info['word']
                    label_for = word_info['for']
                    
                    logger.info(f"第 {round_num} 轮：正在点击第 {i + 1} 个单词: '{word_text}' (for='{label_for}')")
                    print(f"🎯 第 {round_num} 轮：点击第 {i + 1} 个单词: {word_text}")
                    
                    # 多策略点击机制
                    click_success = False
                    
                    # 策略1: 尝试点击label内的checkbox input元素
                    try:
                        checkbox = label.find_element(By.XPATH, ".//input[@type='checkbox']")
                        if checkbox:
                            # 滚动到checkbox元素
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(0.5)
                            
                            # 点击checkbox
                            checkbox.click()
                            click_success = True
                            logger.info(f"第 {round_num} 轮：策略1成功: 点击了checkbox元素")
                    except Exception as e:
                        logger.debug(f"第 {round_num} 轮：策略1失败 (checkbox): {e}")
                    
                    # 策略2: 如果策略1失败，尝试点击span文本元素
                    if not click_success:
                        try:
                            span = label.find_element(By.XPATH, ".//span")
                            if span:
                                # 滚动到span元素
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span)
                                time.sleep(0.5)
                                
                                # 点击span
                                span.click()
                                click_success = True
                                logger.info(f"第 {round_num} 轮：策略2成功: 点击了span元素")
                        except Exception as e:
                            logger.debug(f"第 {round_num} 轮：策略2失败 (span): {e}")
                    
                    # 策略3: 如果前两种策略都失败，直接用JavaScript点击label
                    if not click_success:
                        try:
                            # 滚动到label元素
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                            time.sleep(0.5)
                            
                            # 使用JavaScript直接点击
                            self.driver.execute_script("arguments[0].click();", label)
                            click_success = True
                            logger.info(f"第 {round_num} 轮：策略3成功: 使用JavaScript点击了label元素")
                        except Exception as e:
                            logger.error(f"第 {round_num} 轮：策略3失败 (JavaScript): {e}")
                    
                    if click_success:
                        # 记录点击信息
                        clicked_info = {
                            'word': word_text,
                            'for': label_for,
                            'index': i + 1,
                            'round': round_num
                        }
                        result['clicked_labels'].append(clicked_info)
                        logger.info(f"第 {round_num} 轮：成功点击单词: {word_text}")
                        
                        # 点击间隔
                        time.sleep(random.uniform(0.5, 1.5))
                    else:
                        logger.error(f"第 {round_num} 轮：所有点击策略都失败，跳过单词: '{word_text}' (for='{label_for}')")
                        
                except Exception as e:
                    logger.error(f"第 {round_num} 轮：点击第 {i + 1} 个单词时发生错误: {e}")
                    continue
            
            # 设置所有单词的known状态并添加到结果中
            for word_info in all_words_info:
                word_result = {
                    'word': word_info['word'],
                    'known': word_info['for'] in clicked_for_set,  # 如果被点击则为True
                    'for': word_info['for']
                }
                result['words'].append(word_result)
            
            logger.info(f"第 {round_num} 轮：完成点击操作，成功点击了 {len(result['clicked_labels'])} 个单词")
            print(f"✅ 第 {round_num} 轮：完成点击操作，成功点击了 {len(result['clicked_labels'])} 个单词")
            
            return result
            
        except Exception as e:
            logger.error(f"第 {round_num} 轮：点击单词过程中发生错误: {e}")
            return result
    
    def _click_continue_button(self):
        """
        点击Continue按钮
        
        Returns:
            bool: 点击是否成功
        """
        try:
            logger.info("正在查找Continue按钮...")
            
            # 查找Continue按钮
            continue_button = self.driver.find_element(
                By.XPATH,
                "//button[@data-preply-ds-component='Button' and .//span[text()='Continue']]"
            )
            
            if continue_button:
                # 滚动到按钮
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                time.sleep(0.5)
                
                # 点击按钮
                continue_button.click()
                logger.info("Continue按钮点击成功")
                print("🔄 Continue按钮点击成功")
                return True
            else:
                logger.warning("未找到Continue按钮")
                return False
                
        except Exception as e:
            logger.error(f"点击Continue按钮时发生错误: {e}")
            return False
    
    def _capture_final_vocab_size(self):
        """
        捕获最终词汇量结果
        
        Returns:
            str: 最终词汇量数字，如果未找到则返回None
        """
        try:
            logger.info("正在查找最终词汇量结果...")
            
            # 查找包含最终词汇量的h3元素
            vocab_element = self.driver.find_element(
                By.XPATH,
                "//h3[@class='preply-ds-heading Heading__Lv13n Heading--variant-huge__uNKwX TextCentered__7KaTF TextCentered--centered__4f-qW TextAccent__AfPNQ TextAccent--accent-default__rjbSO Color__vfkGX' and @data-preply-ds-component='Heading']"
            )
            
            if vocab_element:
                vocab_size = vocab_element.text.strip()
                logger.info(f"成功捕获最终词汇量: {vocab_size}")
                return vocab_size
            else:
                logger.warning("未找到最终词汇量元素")
                return None
                
        except Exception as e:
            logger.error(f"捕获最终词汇量时发生错误: {e}")
            # 尝试更宽泛的选择器
            try:
                logger.info("尝试使用更宽泛的选择器查找词汇量...")
                vocab_element = self.driver.find_element(
                    By.XPATH,
                    "//h3[contains(@class, 'preply-ds-heading') and contains(@class, 'Heading--variant-huge')]"
                )
                if vocab_element:
                    vocab_size = vocab_element.text.strip()
                    logger.info(f"使用备用选择器成功捕获最终词汇量: {vocab_size}")
                    return vocab_size
            except Exception as e2:
                logger.error(f"备用选择器也失败: {e2}")
            
            return None
    
    def scrape_target_elements(self):
        """
        抓取目标div元素
        
        Returns:
            list: 找到的元素列表，每个元素包含文本内容和其他属性
        """
        results = []
        
        try:
            # 初始化WebDriver
            self._setup_driver()
            
            logger.info(f"正在访问目标网站: {self.target_url}")
            self.driver.get(self.target_url)
            
            # 等待页面加载
            self._wait_for_page_load()
            
            # 检查并等待Cloudflare验证
            self._wait_for_cloudflare_verification(self.verify_timeout)
            
            # 查找具有指定class属性的div元素
            logger.info(f"正在查找class属性为: {self.target_class}")
            
            # 使用完整的class属性查找
            elements = self.driver.find_elements(
                By.XPATH, 
                f"//div[@class='{self.target_class}']"
            )
            
            if not elements:
                # 如果完整匹配失败，尝试部分匹配
                logger.info("完整class匹配失败，尝试部分匹配...")
                elements = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'LayoutGap__FdLKD') and contains(@class, 'LayoutHide__Q53jS')]"
                )
            
            logger.info(f"找到 {len(elements)} 个匹配的元素")
            
            # 提取元素信息
            for i, element in enumerate(elements):
                try:
                    element_info = {
                        'index': i + 1,
                        'tag_name': element.tag_name,
                        'text': element.text.strip(),
                        'class_attribute': element.get_attribute('class'),
                        'inner_html': element.get_attribute('innerHTML')[:500] + '...' if len(element.get_attribute('innerHTML')) > 500 else element.get_attribute('innerHTML'),
                        'location': element.location,
                        'size': element.size
                    }
                    
                    results.append(element_info)
                    
                    # 打印元素信息
                    print(f"\n=== 元素 {i + 1} ===")
                    print(f"标签名: {element_info['tag_name']}")
                    print(f"文本内容: {element_info['text']}")
                    print(f"Class属性: {element_info['class_attribute']}")
                    print(f"位置: {element_info['location']}")
                    print(f"大小: {element_info['size']}")
                    print(f"HTML内容(前500字符): {element_info['inner_html']}")
                    print("-" * 50)
                    
                except Exception as e:
                    logger.error(f"提取第 {i + 1} 个元素信息时出错: {e}")
            
            return results
            
        except TimeoutException:
            logger.error("页面加载超时")
            return []
        except NoSuchElementException:
            logger.warning("未找到匹配的元素")
            return []
        except Exception as e:
            logger.error(f"抓取过程中发生错误: {e}")
            return []
        finally:
            # 清理资源
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver 已关闭")
    
    def get_page_info(self):
        """
        获取页面基本信息
        
        Returns:
            dict: 页面信息
        """
        try:
            if not self.driver:
                self._setup_driver()
                self.driver.get(self.target_url)
                self._wait_for_page_load()
            
            page_info = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'page_source_length': len(self.driver.page_source)
            }
            
            return page_info
            
        except Exception as e:
            logger.error(f"获取页面信息时出错: {e}")
            return {}
            