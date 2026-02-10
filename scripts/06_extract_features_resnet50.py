import argparse, glob, os
import torch
import pandas as pd
from PIL import Image
from tqdm import tqdm
from torchvision import models, transforms

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="root containing ccrcc/ and chromophobe/")
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device:", device)

    m = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    m.fc = torch.nn.Identity()
    m.eval().to(device)

    prep = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
    ])

    rows = []
    classes = [("ccrcc","ccrcc"), ("chromophobe","chromophobe")]

    with torch.no_grad():
        for class_dir, label in classes:
            slide_dirs = sorted([d for d in glob.glob(os.path.join(args.root, class_dir, "*")) if os.path.isdir(d)])
            print(label, "slides:", len(slide_dirs))

            for sd in slide_dirs:
                sid = os.path.basename(sd.rstrip("/"))
                imgs = sorted(glob.glob(os.path.join(sd, "*.png")) + glob.glob(os.path.join(sd, "*.jpg")))
                if not imgs:
                    continue

                feats = []
                for p in tqdm(imgs, desc=f"{label}:{sid}", leave=False):
                    im = Image.open(p).convert("RGB")
                    x = prep(im).unsqueeze(0).to(device)
                    f = m(x).squeeze(0).cpu()
                    feats.append(f)
                    rows.append([sid, label, os.path.basename(p)] + f.tolist())

                feats = torch.stack(feats) if feats else torch.empty((0,2048))
                torch.save({"slide": sid, "label": label, "features": feats},
                           os.path.join(args.out_dir, f"{sid}_resnet50.pt"))

    if not rows:
        raise SystemExit("No rows produced. Check --root path.")

    D = len(rows[0]) - 3
    cols = ["slide","label","patch"] + [f"f{i}" for i in range(D)]
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(args.out_csv, index=False)
    print("Saved CSV:", args.out_csv, "rows:", len(df), "dim:", D)

if __name__ == "__main__":
    main()
