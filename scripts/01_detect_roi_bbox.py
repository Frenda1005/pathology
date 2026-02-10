import argparse
import cv2
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro", required=True)
    ap.add_argument("--w0", type=int, required=True, help="level0 width")
    ap.add_argument("--h0", type=int, required=True, help="level0 height")
    ap.add_argument("--margin", type=float, default=0.05)
    ap.add_argument("--out_overlay", default=None)
    args = ap.parse_args()

    img = cv2.imread(args.macro)
    if img is None:
        raise SystemExit(f"Cannot read macro: {args.macro}")

    h, w = img.shape[:2]
    b, g, r = cv2.split(img)

    # red pixel heuristic (tune if needed)
    red = (r > 180) & (g < 100) & (b < 100)
    mask = (red.astype(np.uint8) * 255)

    k = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        raise SystemExit("No red ROI contour found")

    cnt = max(cnts, key=cv2.contourArea)
    x, y, w2, h2 = cv2.boundingRect(cnt)
    mx0, my0, mx1, my1 = x, y, x+w2-1, y+h2-1

    sx = args.w0 / w
    sy = args.h0 / h

    X0 = int(mx0 * sx); X1 = int(mx1 * sx)
    Y0 = int(my0 * sy); Y1 = int(my1 * sy)

    # margin
    mxm = int(args.margin * (X1 - X0))
    mym = int(args.margin * (Y1 - Y0))
    X0 = max(0, X0 - mxm); Y0 = max(0, Y0 - mym)
    X1 = min(args.w0-1, X1 + mxm); Y1 = min(args.h0-1, Y1 + mym)

    print("MACRO size:", (w, h))
    print("MACRO roi bbox:", (mx0, my0, mx1, my1))
    print("LEVEL0 bbox (with margin):", (X0, Y0, X1, Y1))

    if args.out_overlay:
        dbg = img.copy()
        cv2.rectangle(dbg, (mx0,my0), (mx1,my1), (0,255,0), 3)
        cv2.imwrite(args.out_overlay, dbg)
        print("Saved overlay:", args.out_overlay)

if __name__ == "__main__":
    main()
