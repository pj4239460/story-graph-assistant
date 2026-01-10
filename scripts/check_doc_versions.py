#!/usr/bin/env python3
"""
文档版本号一致性检查工具

只检查文档中明确标注为"当前版本"的版本号是否与src/__init__.py一致
不检查示例代码、依赖版本、历史版本等其他数字
"""

import re
from pathlib import Path

def get_package_version(base_dir: Path) -> str:
    """从src/__init__.py获取包版本号"""
    init_file = base_dir / "src" / "__init__.py"
    if not init_file.exists():
        return None
    
    content = init_file.read_text(encoding='utf-8')
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        version = match.group(1)
        # 返回主版本号（0.7.0 -> 0.7）
        return version.rsplit('.', 1)[0] if version.count('.') > 1 else version
    return None

def extract_current_version_mentions(text: str) -> list:
    """提取文档中明确标注为"当前版本"的版本号"""
    mentions = []
    
    # 匹配各种"当前版本"的表述
    patterns = [
        r'v(\d+\.\d+)\s*[（(]?(?:Current|当前|current)[)）]?',
        r'v(\d+\.\d+)\s*(?:NEW|新增|最新)',
        r'(?:Current|当前)\s*(?:Version|版本)[:\s]*[vV]?(\d+\.\d+)',
        r'## v(\d+\.\d+)\s+\([^)]*Current[^)]*\)',  # Markdown header
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        mentions.extend(matches)
    
    return list(set(mentions))  # Remove duplicates

def check_file(filepath: Path, expected_version: str) -> dict:
    """检查文件中明确标注的当前版本是否匹配"""
    if not filepath.exists():
        return {"status": "missing"}
    
    try:
        content = filepath.read_text(encoding='utf-8')
        mentions = extract_current_version_mentions(content)
        
        if not mentions:
            return {"status": "ok", "note": "No current version mentioned"}
        
        # 检查是否所有提到的当前版本都匹配
        mismatches = [v for v in mentions if v != expected_version]
        
        return {
            "status": "warning" if mismatches else "ok",
            "mentions": mentions,
            "mismatches": mismatches if mismatches else None
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    """主函数"""
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    
    # 获取包版本号
    package_version = get_package_version(base_dir)
    if not package_version:
        print("[ERROR] Cannot read version from src/__init__.py")
        return 1
    
    print("="*60)
    print("Documentation Version Consistency Check")
    print(f"Package Version: v{package_version}")
    print("="*60)
    print()
    
    # 需要检查的文档文件
    files_to_check = [
        "README.md",
        "GETTING_STARTED.en.md",
        "GETTING_STARTED.zh.md",
        "docs/developer_guide.en.md",
        "docs/world_director_guide.md",
        "docs/world_director_guide.zh.md",
        "docs/INDEX.md",
    ]
    
    issues_found = False
    
    for file_path in files_to_check:
        full_path = base_dir / file_path
        result = check_file(full_path, package_version)
        
        if result["status"] == "missing":
            print(f"[!] {file_path}: File not found")
            issues_found = True
        elif result["status"] == "error":
            print(f"[X] {file_path}: Error - {result['error']}")
            issues_found = True
        elif result["status"] == "warning":
            print(f"[!] {file_path}: Version mismatch")
            print(f"    Expected: v{package_version}")
            print(f"    Found: v{', v'.join(result['mismatches'])}")
            issues_found = True
        else:
            if result.get("note"):
                print(f"[OK] {file_path}: {result['note']}")
            else:
                print(f"[OK] {file_path}: v{package_version}")
    
    print()
    print("="*60)
    if issues_found:
        print("[X] Version inconsistencies found")
        print("Please update the 'Current Version' mentions in the files above")
    else:
        print("[OK] All current version mentions are consistent")
    print("="*60)
    
    return 1 if issues_found else 0

if __name__ == "__main__":
    exit(main())
