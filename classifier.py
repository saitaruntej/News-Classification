"""
=============================================================
  classifier.py  —  Big Data News Classifier 2026
  Stack : Dask (distributed DataFrames)  +  scikit-learn
  Data  : Live 2026 headlines from NewsAPI (news_2026.csv)
=============================================================
  Pipeline:
    1. Load CSV with Dask
    2. Dask map / filter / reduce  (RDD equivalents)
    3. Category distribution chart
    4. Feature engineering  (TF-IDF + bigrams)
    5. Naive Bayes  vs  Weighted Logistic Regression
    6. Evaluation + best model selection
    7. Interactive prediction menu
=============================================================
"""

import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

import dask.dataframe as dd
import pandas as pd
import numpy as np
from collections import Counter

from sklearn.pipeline        import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes     import MultinomialNB
from sklearn.linear_model    import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics         import (accuracy_score,
                                     classification_report,
                                     confusion_matrix)
from sklearn.preprocessing   import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight


# ── DEMO HEADLINES (shown if CSV not found) ───────────────
DEMO_DATA = {
    "headline": [
        "fed raises interest rates to combat rising inflation in 2026",
        "apple unveils new iphone with ai chip and satellite messaging",
        "lebron james scores record points in nba finals game 7",
        "scientists discover potential alzheimer vaccine in breakthrough trial",
        "oscars 2026 ceremony sees record viewership with surprising wins",
        "global leaders meet in dubai for climate summit 2026",
        "nvidia releases blackwell ultra gpu for ai workloads",
        "premier league clubs spend record £3bn in january transfer window",
        "new weight loss drug outperforms ozempic in clinical trials",
        "spacex successfully lands starship on the moon surface",
        "us unemployment hits 50-year low as economy surges",
        "taylor swift announces world tour breaking ticket sales records",
        "who declares new virus variant a global health concern",
        "bitcoin surges past 150000 as etf inflows hit all time high",
        "india wins icc world cup 2026 defeating australia in final",
        "openai releases gpt-5 with real-time reasoning capabilities",
        "parliament passes new data privacy law protecting citizen rights",
        "ronaldo scores 900th career goal in saudi pro league match",
        "nasa artemis crew lands on lunar south pole for first time",
        "amazon acquires major healthcare provider in 10 billion deal",
        "eu bans single-use plastics in sweeping environmental legislation",
        "netflix original film wins best picture at academy awards 2026",
        "researchers develop battery that charges phone in under 2 minutes",
        "ukraine peace talks begin in ankara with us and eu mediation",
        "india launches first crewed space mission to international station",
        "stock market hits record high on strong earnings season",
        "new cancer immunotherapy shows 90% success in clinical trials",
        "microsoft copilot integrated into all windows 12 features",
        "world cup 2026 host cities announced across usa canada mexico",
        "supreme court rules on landmark ai intellectual property case",
        "tropical cyclone hits southeast asia displacing millions",
        "tennis star wins fourth consecutive wimbledon title",
        "inflation cools to 2.1% as central bank holds interest rates",
        "streaming wars intensify as disney plus surpasses netflix subscribers",
        "new mental health legislation mandates coverage for all employees",
        "robot performs successful heart surgery without human assistance",
        "gold prices hit all-time high amid global economic uncertainty",
        "major earthquake strikes pacific ring of fire damaging coastline",
        "olympic committee announces 2030 winter games location",
        "tech layoffs continue as automation replaces white-collar jobs",
    ],
    "category": [
        "BUSINESS", "TECHNOLOGY", "SPORTS", "HEALTH", "ENTERTAINMENT",
        "GENERAL", "TECHNOLOGY", "SPORTS", "HEALTH", "SCIENCE",
        "BUSINESS", "ENTERTAINMENT", "HEALTH", "BUSINESS", "SPORTS",
        "TECHNOLOGY", "GENERAL", "SPORTS", "SCIENCE", "BUSINESS",
        "GENERAL", "ENTERTAINMENT", "TECHNOLOGY", "GENERAL", "SCIENCE",
        "BUSINESS", "HEALTH", "TECHNOLOGY", "SPORTS", "GENERAL",
        "GENERAL", "SPORTS", "BUSINESS", "ENTERTAINMENT", "HEALTH",
        "SCIENCE", "BUSINESS", "GENERAL", "SPORTS", "TECHNOLOGY",
    ]
}


# ─── BANNER ──────────────────────────────────────────────
def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║    BIG DATA NEWS CLASSIFIER  —  Python + Dask 2026      ║
║    TF-IDF + Bigrams | Naive Bayes | Weighted LogReg     ║
╚══════════════════════════════════════════════════════════╝
""")


# ─── 1. LOAD DATA WITH DASK ───────────────────────────────
def load_data(csv_path: str = "combined_news.csv") -> pd.DataFrame:
    """
    Load CSV with Dask (distributed DataFrame).
    Falls back to built-in demo data if CSV not found.
    """
    print("=" * 55)
    print("  STEP 1 — DATA LOADING (Dask Distributed DataFrame)")
    print("=" * 55)

    if os.path.exists(csv_path):
        print(f"\n📂  Loading: {csv_path}")

        # Load with Dask — partitioned across available CPU cores
        ddf = dd.read_csv(
            csv_path,
            usecols=["headline", "category"],
            dtype={"headline": str, "category": str},
            assume_missing=True,
        )

        # Dask transformations (lazy — executed on .compute())
        ddf = ddf.dropna()
        ddf = ddf[ddf["headline"].str.len() > 10]
        ddf = ddf.drop_duplicates(subset=["headline"])

        # Convert to pandas after Dask preprocessing
        df = ddf.compute().reset_index(drop=True)
        df["headline"] = df["headline"].astype(object)
        df["category"] = df["category"].astype(object)
        print(f"  ✅  Dask loaded {len(df):,} rows across "
              f"{ddf.npartitions} partitions")

    else:
        print(f"\n⚠️   '{csv_path}' not found.")
        print("     Using built-in 2026 demo dataset.")
        print("     Run news_fetcher.py to get live data.\n")
        df = pd.DataFrame(DEMO_DATA)

    # Normalise
    df = df.dropna(subset=["headline", "category"])
    df["headline"] = df["headline"].str.lower().str.strip()
    df["category"] = df["category"].str.upper().str.strip()

    print(f"\n  Total records : {len(df):,}")
    print(f"  Categories    : {df['category'].nunique()}")
    return df


# ─── 2. DASK MAP / FILTER / REDUCE (RDD equivalents) ─────
def dask_operations(df: pd.DataFrame):
    """Demonstrate Dask map, filter, reduce — mirrors Spark RDDs."""
    print("\n" + "=" * 55)
    print("  STEP 2 — DASK MAP / FILTER / REDUCE OPERATIONS")
    print("=" * 55)

    # Re-create Dask series from pandas for distributed ops
    dask_series = dd.from_pandas(df["headline"], npartitions=4)

    # map()   → word count per headline
    word_counts = dask_series.map(lambda h: len(str(h).split()))

    # reduce() → total word count
    total_words = word_counts.sum().compute()
    print(f"\n  📊  Total words across all headlines : {total_words:,}")

    # filter() → headlines containing the word "new"
    news_mask    = dask_series.map(lambda h: "new" in str(h).split())
    news_series  = dask_series[news_mask].compute()
    news_count   = len(news_series)
    print(f"  📰  Headlines containing 'new'        : {news_count:,}")

    # map() → word frequency across all headlines
    all_words = (dask_series
                 .map(lambda h: str(h).split())
                 .compute()
                 .explode()
                 )
    top_words = Counter(all_words).most_common(5)
    print(f"\n  🔤  Top 5 most frequent words:")
    for word, cnt in top_words:
        print(f"       {word:<15} {cnt:>5}")

    # Sample headlines table
    samples = news_series.head(3).tolist()
    print(f"\n  Sample headlines containing 'new':")
    print(f"  {'#':<3} {'Headline':<65}")
    print("  " + "─" * 70)
    for i, h in enumerate(samples, 1):
        print(f"  {i:<3} {h[:65]}")


# ─── 3. CATEGORY DISTRIBUTION ────────────────────────────
def show_distribution(df: pd.DataFrame):
    print("\n" + "=" * 55)
    print("  STEP 3 — CATEGORY DISTRIBUTION")
    print("=" * 55)

    counts = df["category"].value_counts()
    max_c  = counts.max()
    bar_w  = 35

    print()
    for cat, cnt in counts.items():
        bars = int((cnt / max_c) * bar_w)
        bar  = "█" * bars
        print(f"  {cat:<16} | {bar:<35} | {cnt:>5}")


# ─── 4. FEATURE ENGINEERING ──────────────────────────────
def build_feature_pipeline(ngram_range=(1, 2), max_features=20_000):
    """
    TF-IDF with unigrams + bigrams.
    Equivalent to Spark's HashingTF + IDF + NGram.
    """
    return TfidfVectorizer(
        lowercase      = True,
        stop_words     = "english",
        ngram_range    = ngram_range,     # (1,2) = unigrams + bigrams
        max_features   = max_features,
        min_df         = 2,               # ignore terms in < 2 docs
        sublinear_tf   = True,            # apply 1+log(tf) scaling
    )


# ─── 5. TRAIN MODELS ─────────────────────────────────────
def train_models(X_train, X_test, y_train, y_test, classes):
    print("\n" + "=" * 55)
    print("  STEP 4 — MODEL TRAINING")
    print("=" * 55)

    results = {}

    # ── A. Naive Bayes ────────────────────────────────────
    print("\n  🔧  Training Naive Bayes …")
    t0 = time.time()

    nb_pipeline = Pipeline([
        ("tfidf", build_feature_pipeline()),
        ("nb",    MultinomialNB(alpha=1.0)),
    ])
    nb_pipeline.fit(X_train, y_train)
    nb_preds   = nb_pipeline.predict(X_test)
    nb_acc     = accuracy_score(y_test, nb_preds)
    nb_time    = time.time() - t0

    results["Naive Bayes"] = {
        "model"   : nb_pipeline,
        "preds"   : nb_preds,
        "accuracy": nb_acc,
        "time"    : nb_time,
    }
    print(f"    ✅  Done in {nb_time:.2f}s  |  Accuracy: {nb_acc*100:.2f}%")

    # ── B. Weighted Logistic Regression ───────────────────
    print("  🔧  Training Weighted Logistic Regression …")
    t0 = time.time()

    # Compute class weights to handle imbalance
    class_weights = compute_class_weight(
        class_weight = "balanced",
        classes      = classes,
        y            = y_train
    )
    weight_dict = dict(zip(classes, class_weights))

    lr_pipeline = Pipeline([
        ("tfidf", build_feature_pipeline()),
        ("lr",    LogisticRegression(
                      max_iter     = 500,
                      C            = 5.0,
                      solver       = "saga",        # fast for large data
                      class_weight = weight_dict,
                      n_jobs       = -1,            # all CPU cores
                  )),
    ])
    lr_pipeline.fit(X_train, y_train)
    lr_preds  = lr_pipeline.predict(X_test)
    lr_acc    = accuracy_score(y_test, lr_preds)
    lr_time   = time.time() - t0

    results["Weighted Logistic Regression"] = {
        "model"   : lr_pipeline,
        "preds"   : lr_preds,
        "accuracy": lr_acc,
        "time"    : lr_time,
    }
    print(f"    ✅  Done in {lr_time:.2f}s  |  Accuracy: {lr_acc*100:.2f}%")

    return results


# ─── 6. EVALUATION ───────────────────────────────────────
def evaluate(results: dict, y_test) -> tuple:
    print("\n" + "=" * 55)
    print("  STEP 5 — MODEL EVALUATION")
    print("=" * 55)

    print(f"\n  {'Model':<35} {'Accuracy':>10}  {'Time':>7}")
    print("  " + "─" * 57)

    best_name  = None
    best_acc   = -1
    best_model = None

    for name, info in results.items():
        acc  = info["accuracy"]
        sec  = info["time"]
        flag = " 🏆" if acc == max(r["accuracy"] for r in results.values()) else ""
        print(f"  {name:<35} {acc*100:>9.2f}%  {sec:>5.2f}s{flag}")

        if acc > best_acc:
            best_acc   = acc
            best_name  = name
            best_model = info["model"]

    # Detailed report for best model
    print(f"\n  📋  Classification Report — {best_name}")
    print("  " + "─" * 55)
    report = classification_report(
        y_test,
        results[best_name]["preds"],
        zero_division=0
    )
    # Indent each line
    for line in report.strip().split("\n"):
        print("  " + line)

    return best_model, best_name, best_acc


# ─── 7. INTERACTIVE PREDICTION MENU ──────────────────────
SAMPLE_HEADLINES_2026 = [
    "rbi cuts interest rates to boost india's gdp growth in 2026",
    "ipl 2026 mega auction breaks all records with new franchises",
    "isro successfully launches gaganyaan crew to lunar orbit",
    "jio announces 6g network rollout across tier 1 cities",
    "india beats pakistan in t20 world cup 2026 final at wankhede",
    "new upi feature allows cross-border payments in 100 countries",
    "scientists find cure for dengue fever in breakthrough pune study",
    "bollywood film crosses 1000 crore box office in record 5 days",
]


def predict(model, headline: str) -> tuple[str, float]:
    """Predict category and confidence for a headline."""
    probs    = model.predict_proba([headline.lower()])[0]
    classes  = model.classes_
    idx      = int(np.argmax(probs))
    return classes[idx], float(probs[idx])


def interactive_menu(model, model_name: str, accuracy: float):
    print("\n" + "=" * 55)
    print("  STEP 6 — INTERACTIVE CLASSIFICATION MENU")
    print("=" * 55)

    while True:
        print("""
  1.  Show model accuracy
  2.  Predict 2026 sample headlines
  3.  Enter your own headline
  4.  Exit
""")
        choice = input("  Enter choice [1-4]: ").strip()

        if choice == "1":
            print(f"\n  Model    : {model_name}")
            print(f"  Accuracy : {accuracy*100:.2f}%\n")

        elif choice == "2":
            print(f"\n  {'Headline':<55} {'Category':<16} {'Conf':>6}")
            print("  " + "─" * 80)
            for h in SAMPLE_HEADLINES_2026:
                cat, conf = predict(model, h)
                print(f"  {h[:54]:<55} {cat:<16} {conf:.2f}")

        elif choice == "3":
            user_hl = input("\n  Enter a 2026 news headline: ").strip()
            if not user_hl:
                print("  ⚠️  Empty input. Try again.")
                continue
            cat, conf = predict(model, user_hl)
            print(f"\n  ✅  Predicted Category : {cat}")
            print(f"      Confidence         : {conf:.4f}  ({conf*100:.1f}%)\n")

        elif choice == "4":
            print("\n  👋  Exiting. Goodbye!\n")
            break

        else:
            print("  ⚠️  Invalid choice. Enter 1, 2, 3 or 4.")


# ─── MAIN ─────────────────────────────────────────────────
def main():
    print_banner()

    # ── 1. Load data
    df = load_data("combined_news.csv")

    # ── 2. Dask RDD-style operations
    dask_operations(df)

    # ── 3. Category distribution
    show_distribution(df)

    # ── 4. Train / test split  (80 / 20)
    print("\n" + "=" * 55)
    print("  TRAIN / TEST SPLIT  (80% / 20%)")
    print("=" * 55)

    X = df["headline"].astype(str).tolist()
    y = df["category"].astype(str).tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size    = 0.2,
        random_state = 42,
        stratify     = y if len(df) >= 40 else None,
    )

    classes = np.unique(y_train)
    print(f"\n  Train: {len(X_train):,}  |  Test: {len(X_test):,}  "
          f"|  Classes: {len(classes)}")

    # ── 5. Train models
    results = train_models(X_train, X_test, y_train, y_test, classes)

    # ── 6. Evaluate
    best_model, best_name, best_acc = evaluate(results, y_test)

    # ── 7. Interactive menu
    # interactive_menu(best_model, best_name, best_acc)


if __name__ == "__main__":
    main()
