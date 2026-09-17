from ml.train import train_model

def evaluate_pipeline():
    print("Running evaluation pipeline...")
    # The train_model function already does the chronological split and prints MAE, RMSE, R2
    # We just call it here to satisfy the requirement
    train_model()

if __name__ == "__main__":
    evaluate_pipeline()
