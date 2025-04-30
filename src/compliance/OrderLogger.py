import boto3, json, datetime as dt, os, logging

_s3 = boto3.client("s3")
_BUCKET = os.getenv("AUDIT_BUCKET", "ai‑trading‑audit")

def log_order(order: dict):
    key = f"orders/{dt.datetime.utcnow().strftime('%Y/%m/%d/%H%M%S_%f')}.json"
    try:
        _s3.put_object(Bucket=_BUCKET, Key=key, Body=json.dumps(order).encode(), ContentType="application/json")
    except Exception as exc:
        logging.exception("Failed to log order: %s", exc)
