import argparse
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score, balanced_accuracy_score, confusion_matrix

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--pos_label", default="ccrcc")
    ap.add_argument("--out", default="/work/dataset/features/slide_predictions_loo.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    feat_cols = [c for c in df.columns if c.startswith("f")]
    slide_feats = df.groupby(["slide","label"])[feat_cols].mean().reset_index()

    y = (slide_feats["label"].values == args.pos_label).astype(int)
    X = slide_feats[feat_cols].values
    slides = slide_feats["slide"].values

    probs = np.zeros(len(slides), dtype=float)
    for i in range(len(slides)):
        train = np.arange(len(slides)) != i
        test  = ~train
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
        clf.fit(X[train], y[train])
        probs[i] = clf.predict_proba(X[test])[0,1]

    pred = (probs >= 0.5).astype(int)

    print("Slides:", len(slides))
    print("AUC:", round(roc_auc_score(y, probs), 3))
    print("Accuracy:", round(accuracy_score(y, pred), 3))
    print("Balanced Acc:", round(balanced_accuracy_score(y, pred), 3))
    print("Confusion matrix (rows=true [neg,pos], cols=pred [neg,pos]):")
    print(confusion_matrix(y, pred))

    out = pd.DataFrame({
        "slide": slides,
        "true_label": np.where(y==1,args.pos_label,"other"),
        "p_pos": probs,
        "pred_label": np.where(pred==1,args.pos_label,"other")
    }).sort_values("p_pos", ascending=False)

    out.to_csv(args.out, index=False)
    print("Saved:", args.out)

if __name__ == "__main__":
    main()
