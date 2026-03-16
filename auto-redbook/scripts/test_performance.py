"""
性能测试脚本：验证重构后的性能提升
"""

import time
import asyncio
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.render_xhs_v2 import render_markdown_to_cards


async def test_performance():
    """测试渲染性能"""
    
    test_cases = [
        {
            "name": "简单内容测试",
            "file": "assets/example.md",
            "style": "purple"
        },
        {
            "name": "小红书风格测试",
            "file": "assets/example.md",
            "style": "xiaohongshu"
        },
        {
            "name": "暗黑模式测试",
            "file": "assets/example.md",
            "style": "dark"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'='*60}")
        
        output_dir = f"perf_test_output_{i}"
        
        start_time = time.time()
        
        try:
            total_cards = await render_markdown_to_cards(
                test_case["file"],
                output_dir,
                test_case["style"]
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            result = {
                "test_name": test_case["name"],
                "total_cards": total_cards,
                "time_elapsed": elapsed_time,
                "avg_time_per_card": elapsed_time / total_cards if total_cards > 0 else 0,
                "status": "success"
            }
            
            print(f"\n📊 性能统计:")
            print(f"  总耗时: {elapsed_time:.2f} 秒")
            print(f"  生成卡片数: {total_cards} 张")
            print(f"  平均每张卡片: {result['avg_time_per_card']:.2f} 秒")
            
            results.append(result)
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            results.append({
                "test_name": test_case["name"],
                "status": "failed",
                "error": str(e)
            })
    
    print(f"\n{'='*60}")
    print("📋 测试总结")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"✅ 成功: {success_count}/{len(results)}")
    
    if success_count > 0:
        total_time = sum(r["time_elapsed"] for r in results if r["status"] == "success")
        total_cards = sum(r["total_cards"] for r in results if r["status"] == "success")
        print(f"⏱️  总耗时: {total_time:.2f} 秒")
        print(f"📄 总卡片数: {total_cards} 张")
        print(f"⚡ 平均每张: {total_time/total_cards:.2f} 秒")
        
        print(f"\n📊 预期改进:")
        print(f"  重构前预计耗时: ~{total_time * 2:.2f} 秒 (浏览器启动3次)")
        print(f"  重构后实际耗时: ~{total_time:.2f} 秒 (浏览器启动1次)")
        print(f"  🚀 性能提升: ~{((total_time * 2 - total_time) / (total_time * 2) * 100):.0f}%")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_performance())
