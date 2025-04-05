#!/usr/bin/env python3
"""
Plugin Test Script - Tests all direct streaming plugins to check if they're working
"""

import os
import sys
import time
import json
import logging
import argparse
import concurrent.futures
from datetime import datetime

# Import the plugin registry
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from plugin_registry import registry
from plugin_loader import auto_register_platforms

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"plugin_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Test URLs for different platforms
TEST_URLS = {
    "douyu": "https://www.douyu.com/9999",  # 斗鱼
    "huya": "https://www.huya.com/333003",  # 虎牙
    "bilibili": "https://live.bilibili.com/1849256543",  # B站
    # Add more platforms as needed
}

class TestResult:
    """Test result tracker class"""
    def __init__(self):
        self.success = []
        self.failure = []
        self.skipped = []
        self.total = 0
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = time.time()
        
    def finish(self):
        self.end_time = time.time()
    
    @property
    def duration(self):
        if not self.end_time or not self.start_time:
            return 0
        return self.end_time - self.start_time
    
    @property
    def success_rate(self):
        if self.total == 0:
            return 0
        return (len(self.success) / self.total) * 100
    
    def to_dict(self):
        return {
            "success": self.success,
            "failure": self.failure,
            "skipped": self.skipped,
            "total": self.total,
            "success_rate": f"{self.success_rate:.2f}%",
            "duration": f"{self.duration:.2f} seconds"
        }

def test_plugin(platform, url):
    """Test a single plugin with its URL"""
    logger.info(f"Testing {platform} with URL: {url}")
    
    plugin = registry.get_plugin_for_url(url)
    if not plugin:
        logger.error(f"No plugin found for {platform} URL: {url}")
        return {"platform": platform, "status": "FAILURE", "reason": "No plugin found for URL", "url": url}
    
    try:
        start_time = time.time()
        result = plugin.get_real_url(url)
        elapsed = time.time() - start_time
        
        if not result:
            logger.error(f"Failed to get stream URL for {platform}")
            return {
                "platform": platform, 
                "status": "FAILURE",
                "reason": "Plugin returned no result",
                "url": url,
                "time": f"{elapsed:.2f}s"
            }
        
        logger.info(f"Successfully got stream for {platform} in {elapsed:.2f}s")
        return {
            "platform": platform,
            "status": "SUCCESS",
            "url": url,
            "time": f"{elapsed:.2f}s",
            "result_type": type(result).__name__
        }
        
    except Exception as e:
        logger.error(f"Exception in {platform} plugin: {str(e)}")
        return {
            "platform": platform,
            "status": "FAILURE",
            "reason": str(e),
            "url": url,
            "exception": type(e).__name__
        }

def run_tests(platforms=None, parallel=True, max_workers=5):
    """Run tests for all or specified platforms"""
    results = TestResult()
    results.start()
    
    if not auto_register_platforms():
        logger.error("Failed to register platforms. Exiting.")
        return results
    
    test_platforms = platforms or list(TEST_URLS.keys())
    results.total = len(test_platforms)
    
    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for platform in test_platforms:
                if platform not in TEST_URLS:
                    logger.warning(f"No test URL defined for {platform}, skipping")
                    results.skipped.append({"platform": platform, "reason": "No test URL defined"})
                    continue
                    
                futures[executor.submit(test_plugin, platform, TEST_URLS[platform])] = platform
                
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result["status"] == "SUCCESS":
                    results.success.append(result)
                else:
                    results.failure.append(result)
    else:
        for platform in test_platforms:
            if platform not in TEST_URLS:
                logger.warning(f"No test URL defined for {platform}, skipping")
                results.skipped.append({"platform": platform, "reason": "No test URL defined"})
                continue
                
            result = test_plugin(platform, TEST_URLS[platform])
            if result["status"] == "SUCCESS":
                results.success.append(result)
            else:
                results.failure.append(result)
    
    results.finish()
    return results

def generate_report(results):
    """Generate a human-readable report from test results"""
    report = []
    report.append("=" * 80)
    report.append(f"PLUGIN TEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append(f"Total platforms tested: {results.total}")
    report.append(f"Success rate: {results.success_rate:.2f}%")
    report.append(f"Test duration: {results.duration:.2f} seconds")
    report.append("-" * 80)
    
    if results.success:
        report.append("\nSUCCESSFUL PLUGINS:")
        for item in results.success:
            report.append(f"  ✅ {item['platform']} ({item['time']})")
    
    if results.failure:
        report.append("\nFAILED PLUGINS:")
        for item in results.failure:
            reason = item.get('reason', 'Unknown error')
            report.append(f"  ❌ {item['platform']} - {reason}")
    
    if results.skipped:
        report.append("\nSKIPPED PLUGINS:")
        for item in results.skipped:
            report.append(f"  ⚠️ {item['platform']} - {item['reason']}")
    
    report.append("\n" + "=" * 80)
    report.append("PLUGIN IMPROVEMENT RECOMMENDATIONS:")
    report.append("-" * 80)
    
    if results.failure:
        for item in results.failure:
            if 'exception' in item:
                report.append(f"- {item['platform']}: Update to handle {item['exception']} exception")
            else:
                report.append(f"- {item['platform']}: Fix issues with URL extraction or API changes")
    else:
        report.append("All tested plugins are working correctly!")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Test live streaming platform plugins')
    parser.add_argument('-p', '--platforms', nargs='+', help='Specific platforms to test')
    parser.add_argument('-s', '--sequential', action='store_true', help='Run tests sequentially instead of in parallel')
    parser.add_argument('-w', '--workers', type=int, default=5, help='Number of worker threads for parallel testing')
    parser.add_argument('-o', '--output', help='Output file for test results (JSON format)')
    args = parser.parse_args()

    logger.info("Starting plugin tests")
    results = run_tests(
        platforms=args.platforms,
        parallel=not args.sequential,
        max_workers=args.workers
    )
    
    # Generate report
    report = generate_report(results)
    logger.info("\n" + report)
    
    # Save JSON results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Results saved to {args.output}")
    
    return 0 if results.failure else 0

if __name__ == "__main__":
    sys.exit(main()) 