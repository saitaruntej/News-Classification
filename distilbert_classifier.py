import os
import json
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from classifier import load_data
from datasets import Dataset

MODEL_DIR = "./model_output"
NUM_EPOCHS = 3

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

def main():
    print("=" * 55)
    print("  DISTILBERT CLASSIFIER TRAINING")
    print("=" * 55)

    print("Loading data...")
    df = load_data("combined_news.csv")
    
    if len(df) == 0:
        print("No data available.")
        return

    # Map categories to IDs
    categories = df["category"].unique().tolist()
    label2id = {c: i for i, c in enumerate(categories)}
    id2label = {i: c for i, c in enumerate(categories)}
    
    df["label"] = df["category"].map(label2id)
    
    print(f"Categories ({len(categories)}): {categories}")
    
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"] if len(df) > 10 else None)
    
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    def tokenize_data(data_df):
        encodings = tokenizer(data_df['headline'].tolist(), truncation=True, padding=True, max_length=128)
        return Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': data_df['label'].tolist()
        })
        
    train_dataset = tokenize_data(train_df)
    test_dataset = tokenize_data(test_df)
    
    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased', 
        num_labels=len(categories),
        id2label=id2label,
        label2id=label2id
    )
    
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )
    
    print("Training model...")
    trainer.train()
    
    print("Evaluating model...")
    results = trainer.evaluate()
    print(f"Accuracy: {results['eval_accuracy']*100:.2f}%")
    
    print(f"Saving model to {MODEL_DIR}...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    
    # Save label mapping for inference
    with open(os.path.join(MODEL_DIR, "label_mapping.json"), "w") as f:
        json.dump({"label2id": label2id, "id2label": id2label}, f)
    
    print("✅ Training complete.")

if __name__ == "__main__":
    main()
