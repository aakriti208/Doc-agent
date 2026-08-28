from strands.models.bedrock import BedrockModel
from strands.models.model import CacheConfig


def load_model() -> BedrockModel:
    """Get Bedrock model client using IAM credentials."""
    return BedrockModel(
        model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        cache_config=CacheConfig(strategy="auto"),
        cache_tools="default",
    )
