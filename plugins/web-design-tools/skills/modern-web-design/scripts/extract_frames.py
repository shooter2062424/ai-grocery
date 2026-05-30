#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_frames.py — 把「捲動逐幀動畫」需要的幀序列準備好(零補位連號)。

兩種輸入:
  A) 影片  → 用 ffmpeg 拆成 frame_0001.png ...(需本機有 ffmpeg)
  B) 既有幀資料夾(例如已用 ezgif 拆好)→ 依檔名排序、重新命名成零補位連號

輸出固定為:<out>/frame_0001.png, frame_0002.png, ...  方便 ScrollTrigger 元件用。

用法:
  python extract_frames.py --video burger.mp4 --out public/frames/burger --fps 30
  python extract_frames.py --frames-dir ./my_frames --out public/frames/burger
  python extract_frames.py --video in.mp4 --out out/ --webp        # 另存 webp(更小)
"""
import argparse, os, sys, shutil, subprocess, glob, re

IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def have_ffmpeg():
    return shutil.which("ffmpeg") is not None


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def from_video(video, out, fps, ext):
    if not have_ffmpeg():
        sys.exit("ERROR: 找不到 ffmpeg。請先安裝 ffmpeg(https://ffmpeg.org)再重試,或改用 --frames-dir。")
    if not os.path.isfile(video):
        sys.exit(f"ERROR: 影片不存在:{video}")
    os.makedirs(out, exist_ok=True)
    pattern = os.path.join(out, f"frame_%04d.{ext}")
    cmd = ["ffmpeg", "-y", "-i", video, "-vf", f"fps={fps}", pattern]
    print("執行:", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("ERROR: ffmpeg 拆幀失敗。")
    n = len(glob.glob(os.path.join(out, f"frame_*.{ext}")))
    print(f"完成:{n} 幀 → {out}")
    print(f"提示:把 ScrollTrigger 元件的 FRAME_COUNT 設為 {n}。")


def from_dir(frames_dir, out, ext):
    if not os.path.isdir(frames_dir):
        sys.exit(f"ERROR: 資料夾不存在:{frames_dir}")
    files = [f for f in os.listdir(frames_dir) if f.lower().endswith(IMG_EXTS)]
    files.sort(key=natural_key)
    if not files:
        sys.exit(f"ERROR: 資料夾裡找不到圖片:{frames_dir}")
    os.makedirs(out, exist_ok=True)
    for i, f in enumerate(files, 1):
        dst = os.path.join(out, f"frame_{i:04d}.{ext}")
        src = os.path.join(frames_dir, f)
        # 副檔名相同就複製;不同則嘗試用 Pillow 轉檔
        if f.lower().endswith("." + ext):
            shutil.copyfile(src, dst)
        else:
            try:
                from PIL import Image
                Image.open(src).save(dst)
            except Exception:
                # 沒有 Pillow 或轉檔失敗:直接複製,保留原副檔名
                shutil.copyfile(src, os.path.join(out, f"frame_{i:04d}{os.path.splitext(f)[1]}"))
    print(f"完成:{len(files)} 幀 → {out}")
    print(f"提示:把 ScrollTrigger 元件的 FRAME_COUNT 設為 {len(files)}。")


def main():
    ap = argparse.ArgumentParser(description="準備捲動逐幀動畫的幀序列")
    ap.add_argument("--video", help="輸入影片(mp4 等),用 ffmpeg 拆幀")
    ap.add_argument("--frames-dir", help="既有幀資料夾(改成零補位連號)")
    ap.add_argument("--out", required=True, help="輸出資料夾")
    ap.add_argument("--fps", type=int, default=30, help="拆幀的每秒張數(預設 30)")
    ap.add_argument("--webp", action="store_true", help="輸出 webp(更小);預設 png")
    args = ap.parse_args()

    ext = "webp" if args.webp else "png"
    if args.video:
        from_video(args.video, args.out, args.fps, ext)
    elif args.frames_dir:
        from_dir(args.frames_dir, args.out, ext)
    else:
        sys.exit("ERROR: 請提供 --video 或 --frames-dir 其中一個。")


if __name__ == "__main__":
    main()
