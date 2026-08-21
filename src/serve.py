from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import boto3

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "dvc")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """Tai file model.joblib tu cloud storage (S3 / DagsHub / GCS) ve may khi server khoi dong."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # 1. Thu tai qua S3 / DagsHub neu co bien S3/AWS
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL") or os.environ.get("S3_ENDPOINT_URL")
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    
    if aws_access_key and aws_secret_key:
        s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )
        s3_client.download_file(ARTIFACT_BUCKET, MODEL_KEY, MODEL_PATH)
        print("Model da duoc tai xuong tu S3/DagsHub storage.")
        return

    # 2. Thu tai qua Google Cloud Storage
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(ARTIFACT_BUCKET)
        blob = bucket.blob(MODEL_KEY)
        blob.download_to_filename(MODEL_PATH)
        print("Model da duoc tai xuong tu Google Cloud Storage.")
        return
    except Exception as e:
        print(f"Warning: Khong the tai model tu GCS: {e}")


if not os.path.exists(MODEL_PATH):
    try:
        download_model()
    except Exception as e:
        print(f"Warning: {e}")

model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
elif os.path.exists("models/model.joblib"):
    model = joblib.load("models/model.joblib")


FEATURE_NAMES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")

    global model
    if model is None:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
        elif os.path.exists("models/model.joblib"):
            model = joblib.load("models/model.joblib")
        else:
            raise HTTPException(status_code=500, detail="Model is not loaded")

    import pandas as pd
    df_features = pd.DataFrame([req.features], columns=FEATURE_NAMES)
    pred = int(model.predict(df_features)[0])
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"

    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
