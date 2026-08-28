"""
Quick smoke-test for prompt caching and semantic caching.

Run from the app directory with the venv active:
    python test_caching.py
"""

import os, sys, json, asyncio
os.environ.setdefault("AWS_REGION", "us-east-1")

# ── 1. Semantic cache unit test (pure logic, no agent needed) ─────────────────

def test_semantic_cache():
    print("\n=== Semantic Cache ===")
    from cache.semantic_cache import get_cached_response, store_response, _cache

    # Should be empty at start
    assert get_cached_response("hello") is None, "Cache should be empty initially"
    print("✓ Empty cache → miss")

    # Store a response
    store_response("What is prompt caching?", "Prompt caching saves tokens by reusing static prefixes.")
    print("✓ Stored response for 'What is prompt caching?'")

    # Exact same query → hit
    result = get_cached_response("What is prompt caching?")
    assert result is not None, "Expected cache hit for identical query"
    print(f"✓ Identical query → hit: '{result[:60]}...'")

    # Semantically similar query → hit (same embedding space)
    result2 = get_cached_response("How does prompt caching work?")
    if result2:
        print(f"✓ Similar query   → hit: '{result2[:60]}...'")
    else:
        print("  Similar query   → miss (below threshold — consider lowering SEMANTIC_CACHE_THRESHOLD)")

    # Completely unrelated query → miss
    result3 = get_cached_response("What is the weather in Seattle today?")
    assert result3 is None, f"Expected miss for unrelated query, got: {result3}"
    print("✓ Unrelated query → miss")

    print(f"  Cache size: {len(_cache)} entry/entries")
    print("Semantic cache: PASSED\n")


# ── 2. Prompt caching smoke test (needs Bedrock access) ───────────────────────

def test_prompt_cache_config():
    print("=== Prompt Cache Config ===")
    from model.load import load_model
    from strands.models.model import CacheConfig

    model = load_model()
    cfg = model.config

    assert "cache_config" in cfg, "cache_config missing from model config"
    assert isinstance(cfg["cache_config"], CacheConfig), "cache_config should be a CacheConfig instance"
    assert cfg["cache_config"].strategy == "auto", f"Expected strategy='auto', got {cfg['cache_config'].strategy}"
    assert cfg.get("cache_tools") == "default", f"Expected cache_tools='default', got {cfg.get('cache_tools')}"

    print("✓ CacheConfig(strategy='auto') set on model")
    print("✓ cache_tools='default' set on model")
    print("Prompt cache config: PASSED\n")


if __name__ == "__main__":
    try:
        test_prompt_cache_config()
    except Exception as e:
        print(f"✗ Prompt cache config FAILED: {e}\n")

    try:
        test_semantic_cache()
    except Exception as e:
        print(f"✗ Semantic cache FAILED: {e}\n")
        import traceback; traceback.print_exc()

    print("─" * 50)
    print("Next: end-to-end test")
    print("  Terminal 1:  agentcore dev")
    print('  Terminal 2:  agentcore invoke --dev "What is prompt caching?"')
    print('               agentcore invoke --dev "How does prompt caching work?"')
    print("  Second call should return instantly (semantic cache hit) or show")
    print("  cacheReadInputTokens > 0 in logs (prompt cache hit).")
