"""一键更新 SREF 资料库：抓取 → 合并去重 → 重建页面数据 → 补缩略图 → 生成报告。

用法:
  python scripts/update_srefs.py                 # 全量更新（含 Midlibrary）
  python scripts/update_srefs.py --fast          # 只更新两个主要来源，跳过 Midlibrary
  python scripts/update_srefs.py --only srefmj   # 只跑某个来源
  python scripts/update_srefs.py --skip-thumbs   # 不补缩略图
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable or "python"


def run(title, args):
    print(f"\n=== {title} ===", flush=True)
    t0 = time.time()
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([PY, "-u"] + args, cwd=ROOT, env=env)
    ok = p.returncode == 0
    print(f"--- {title}: {'完成' if ok else '失败'}，用时 {time.time()-t0:.0f}s ---", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="跳过 Midlibrary（更快）")
    ap.add_argument("--only", choices=["srefmj", "srefhunt", "midlibrary"], help="只更新一个来源")
    ap.add_argument("--skip-thumbs", action="store_true")
    ap.add_argument("--no-report", action="store_true")
    args = ap.parse_args()

    started = time.time()
    ok = True
    only = args.only

    if only in (None, "srefmj"):
        ok &= run("抓取 Sref-Midjourney", ["scripts/fetch_srefmj.py", "--workers", "3"])
        ok &= run("补齐缺失页", ["scripts/repair_srefmj.py"])
    if only in (None, "srefhunt"):
        ok &= run("抓取 SrefHunt", ["scripts/fetch_srefhunt.py"])
    if only in (None, "midlibrary") and not args.fast:
        ok &= run("抓取 Midlibrary", ["scripts/fetch_midlibrary.py", "--workers", "3"])
        ok &= run("抓取 Midlibrary Look terms（细分类型）",
                  ["scripts/fetch_midlibrary_terms.py", "--workers", "8"])

    cmd = ["scripts/build_library.py"]
    if not args.no_report:
        cmd.append("--report")
    ok &= run("合并去重并生成数据", cmd)

    if not args.skip_thumbs:
        ok &= run("补齐 Midlibrary 缩略图", ["scripts/fetch_thumbs.py", "--workers", "5"])
        ok &= run("本地化远程缩略图（离线可用）", ["scripts/fetch_remote_thumbs.py", "--workers", "8"])

    print(f"\n全部流程{'完成' if ok else '存在失败项'}，总用时 {(time.time()-started)/60:.1f} 分钟", flush=True)
    print("打开 index.html 即可浏览最新结果。", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
