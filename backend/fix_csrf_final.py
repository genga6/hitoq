#!/usr/bin/env python3
"""
CSRFテストの最終修正スクリプト
"""

import re
from pathlib import Path


def fix_test_file(file_path):
    """テストファイルを修正する"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # 1. headers=csrf_headersを使用しているがパラメータにcsrf_headersがない関数を修正
    def fix_function_parameters(content):
        lines = content.split("\n")
        result_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # test_関数の定義行を探す
            if re.match(r"\s*def test_[^(]+\([^)]*\):", line):
                # この関数内でheaders=csrf_headersを使用しているかチェック
                function_lines = [line]
                i += 1

                # 関数の終わりまで読む
                indent_level = len(line) - len(line.lstrip())
                while i < len(lines):
                    current_line = lines[i]

                    # 次の関数またはクラスの開始（同じまたは少ないインデント）
                    if (
                        current_line.strip()
                        and len(current_line) - len(current_line.lstrip())
                        <= indent_level
                        and (
                            current_line.strip().startswith("def ")
                            or current_line.strip().startswith("class ")
                        )
                    ):
                        break

                    function_lines.append(current_line)
                    i += 1

                function_content = "\n".join(function_lines)

                # headers=csrf_headersを使用しているか？
                if "headers=csrf_headers" in function_content:
                    # 関数定義にcsrf_headersパラメータがあるか？
                    if "csrf_headers" not in function_lines[0]:
                        # パラメータを追加
                        func_def = function_lines[0]
                        if func_def.rstrip().endswith("):"):
                            # パラメータがない場合
                            if "()" in func_def:
                                func_def = func_def.replace("():", "(csrf_headers):")
                            else:
                                # 他のパラメータがある場合
                                func_def = func_def.replace("):", ", csrf_headers):")
                        function_lines[0] = func_def

                result_lines.extend(function_lines)
            else:
                result_lines.append(line)
                i += 1

        return "\n".join(result_lines)

    content = fix_function_parameters(content)

    # 2. POST/PUT/DELETE/PATCHリクエストでheaders=csrf_headersが欠けているものを修正
    for method in ["post", "put", "delete", "patch"]:
        # パターン1: client.method("path", json=data) でheadersがない
        pattern1 = rf'(\s+response\s*=\s*client\.{method}\s*\(\s*"[^"]*"\s*,\s*json\s*=\s*[^,)]+)(\))'

        def replacement1(match):
            if "headers=" not in match.group(0):
                return match.group(1) + ", headers=csrf_headers" + match.group(2)
            return match.group(0)

        content = re.sub(pattern1, replacement1, content)

        # パターン2: client.method("path") でheadersがない
        pattern2 = rf'(\s+response\s*=\s*client\.{method}\s*\(\s*"[^"]*")(\))'

        def replacement2(match):
            if "headers=" not in match.group(0):
                return match.group(1) + ", headers=csrf_headers" + match.group(2)
            return match.group(0)

        content = re.sub(pattern2, replacement2, content)

    # 3. csrf_headersがundefinedエラーが出る場合の対処
    # NameError: name 'csrf_headers' is not defined の行を探す
    if "headers=csrf_headers" in content:
        # テストクラス内の関数で csrf_headers パラメータがない場合を修正
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if (
                "def test_" in line
                and "csrf_headers" not in line
                and i < len(lines) - 10
            ):
                # この関数の中でheaders=csrf_headersを使用しているかチェック
                function_content = ""
                j = i + 1
                indent_level = len(line) - len(line.lstrip())
                while j < len(lines):
                    next_line = lines[j]
                    if (
                        next_line.strip()
                        and len(next_line) - len(next_line.lstrip()) <= indent_level
                        and ("def " in next_line or "class " in next_line)
                    ):
                        break
                    function_content += next_line + "\n"
                    j += 1

                if "headers=csrf_headers" in function_content:
                    # パラメータを追加
                    if line.rstrip().endswith("):"):
                        if "()" in line:
                            lines[i] = line.replace("():", "(csrf_headers):")
                        else:
                            lines[i] = line.replace("):", ", csrf_headers):")

        content = "\n".join(lines)

    # ファイルが変更された場合のみ書き込み
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False


def main():
    """メイン実行関数"""
    test_dir = Path(__file__).parent / "test" / "integration" / "router"

    if not test_dir.exists():
        print(f"Test directory not found: {test_dir}")
        return

    fixed_files = 0

    for test_file in test_dir.glob("test_*.py"):
        if fix_test_file(test_file):
            fixed_files += 1

    print(f"\nFixed {fixed_files} test files")


if __name__ == "__main__":
    main()
