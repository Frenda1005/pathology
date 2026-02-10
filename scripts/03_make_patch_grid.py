import argparse, glob, os
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tile_dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--thumb", type=int, default=128)
    ap.add_argument("--cols", type=int, default=10)
    args = ap.parse_args()

    imgs = sorted(glob.glob(os.path.join(args.tile_dir, "*.png")) + glob.glob(os.path.join(args.tile_dir, "*.jpg")))
    if not imgs:
        raise SystemExit("No tiles found")

    step = max(1, len(imgs)//args.n)
    imgs = imgs[::step][:args.n]

    thumbs = [Image.open(p).convert("RGB").resize((args.thumb,args.thumb)) for p in imgs]
    rows = (len(thumbs)+args.cols-1)//args.cols
    grid = Image.new("RGB", (args.cols*args.thumb, rows*args.thumb), (255,255,255))
    for i,im in enumerate(thumbs):
        r,c = divmod(i,args.cols)
        grid.paste(im,(c*args.thumb,r*args.thumb))
    grid.save(args.out)
    print("Saved:", args.out)

if __name__ == "__main__":
    main()
