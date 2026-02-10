import argparse, glob, os
import numpy as np
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tile_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--white_thr", type=int, default=235)
    ap.add_argument("--white_frac", type=float, default=0.75)
    ap.add_argument("--black_thr", type=int, default=20)
    ap.add_argument("--black_frac", type=float, default=0.20)
    ap.add_argument("--min_std", type=float, default=8.0)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    imgs = glob.glob(os.path.join(args.tile_dir, "*.png")) + glob.glob(os.path.join(args.tile_dir, "*.jpg"))
    keep = 0

    for p in imgs:
        im = Image.open(p).convert("RGB")
        arr = np.asarray(im).astype(np.uint8)
        gray = arr.mean(axis=2)
        wf = (gray > args.white_thr).mean()
        bf = (gray < args.black_thr).mean()
        std = arr.reshape(-1,3).std(axis=0).mean()

        if wf < args.white_frac and bf < args.black_frac and std > args.min_std:
            keep += 1
            im.save(os.path.join(args.out_dir, os.path.basename(p)))

    print("Total:", len(imgs))
    print("Kept:", keep)
    print("Saved:", args.out_dir)

if __name__ == "__main__":
    main()
