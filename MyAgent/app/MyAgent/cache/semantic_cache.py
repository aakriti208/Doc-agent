import json
import logging
import os
import numpy as np
import boto3

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = float(os.environ.get("SEMANTIC_CACHE_THRESHOLD", "0.92"))
CACHE_MAX_SIZE = 500
_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

_bedrock = None
_cache: list[dict] = []  # [{"embedding": [...], "response": "..."}]


def _get_bedrock():
    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return _bedrock


def _embed(text: str) -> list[float]:
    resp = _get_bedrock().invoke_model(
        modelId=_EMBEDDING_MODEL_ID,
        body=json.dumps({"inputText": text, "dimensions": 512, "normalize": True}),
        contentType="application/json",
        accept="application/json",
    )
    return json.loads(resp["body"].read())["embedding"]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def get_cached_response(query: str) -> str | None:
    if not _cache:
        return None
    try:
        query_emb = _embed(query)
    except Exception:
        logger.warning("Semantic cache: embedding failed, skipping cache lookup", exc_info=True)
        return None
    best_score, best_entry = 0.0, None
    for entry in _cache:
        score = _cosine_similarity(query_emb, entry["embedding"])
        if score > best_score:
            best_score, best_entry = score, entry
    if best_score >= SIMILARITY_THRESHOLD and best_entry is not None:
        logger.info("Semantic cache hit (score=%.3f)", best_score)
        return best_entry["response"]
    return None


def store_response(query: str, response: str):
    try:
        embedding = _embed(query)
    except Exception:
        logger.warning("Semantic cache: embedding failed, skipping cache store", exc_info=True)
        return
    if len(_cache) >= CACHE_MAX_SIZE:
        _cache.pop(0)
    _cache.append({"embedding": embedding, "response": response})
