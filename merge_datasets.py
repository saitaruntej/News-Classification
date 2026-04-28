import pandas as pd
import json

def merge_datasets():
    print("Loading old dataset...")
    df_old = pd.read_csv("news_2026.csv")
    print(f"Old dataset rows: {len(df_old)}")
    
    print("Loading new dataset...")
    new_data = []
    with open("new_dataset/News_Category_Dataset_v3.json", "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            new_data.append({"headline": item["headline"], "category": item["category"]})
    
    df_new = pd.DataFrame(new_data)
    print(f"New dataset rows: {len(df_new)}")
    
    print("Combining datasets...")
    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    
    # Drop duplicates
    df_combined.drop_duplicates(subset=['headline'], inplace=True)
    print(f"Combined dataset rows (after deduplication): {len(df_combined)}")
    
    df_combined.to_csv("combined_news.csv", index=False)
    print("Saved combined dataset to combined_news.csv")

if __name__ == "__main__":
    merge_datasets()
