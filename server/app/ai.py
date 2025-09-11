"""OpenAI integration for note analysis and embeddings."""

import json
import logging
from typing import Dict, List, Any
from openai import OpenAI, AzureOpenAI
from .config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
if settings.USE_AZURE_OPENAI:
    client = AzureOpenAI(
        api_key=settings.OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )
else:
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE_URL)

# Structured output schema for note analysis
ANALYZE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "NoteAnalysis",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["summary", "tags", "followups"],
            "properties": {
                "summary": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 6},
                "followups": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 3},
            },
        },
    },
}

SYSTEM_PROMPT = """You turn raw notes into:
1) a 1–2 sentence, concrete summary,
2) 3–6 lowercase topical tags,
3) exactly three short, actionable follow-ups (imperative voice).
Be concise and practical. No boilerplate."""


class AIError(Exception):
    """Custom exception for AI-related errors."""

    pass


def analyze_note(title: str, body: str) -> Dict[str, Any]:
    """
    Analyze a note using OpenAI to generate summary, tags, and follow-ups.

    Args:
        title: Note title
        body: Note body content

    Returns:
        Dictionary containing summary, tags, and followups

    Raises:
        AIError: If OpenAI API call fails or returns invalid data
    """
    try:
        # Combine title and body for analysis
        note_text = f"Title: {title}\n\nContent: {body}"

        # Truncate input if too long (approximate token limit)
        if len(note_text) > 8000:  # Conservative estimate for token limit
            note_text = note_text[:8000] + "..."
            logger.warning("Note text truncated to 8000 characters")

        logger.info(f"Analyzing note with {len(note_text)} characters")

        # Call OpenAI with structured output
        response = client.chat.completions.create(
            model=settings.OPENAI_GEN_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": note_text}],
            response_format=ANALYZE_SCHEMA,
            timeout=30,
        )

        # Parse the structured response
        content = response.choices[0].message.content
        if not content:
            raise AIError("Empty response from OpenAI")

        analysis = json.loads(content)

        # Validate the response structure
        if not all(key in analysis for key in ["summary", "tags", "followups"]):
            raise AIError("Invalid response structure from OpenAI")

        # Ensure tags are lowercase
        analysis["tags"] = [tag.lower().strip() for tag in analysis["tags"]]

        logger.info(f"Successfully analyzed note: {len(analysis['tags'])} tags, {len(analysis['followups'])} followups")
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        raise AIError(f"Invalid JSON response from OpenAI: {e}")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise AIError(f"Failed to analyze note: {e}")


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI embeddings API.

    Args:
        text: Text to embed

    Returns:
        List of embedding values

    Raises:
        AIError: If OpenAI API call fails
    """
    try:
        # Truncate text if too long
        if len(text) > 8000:
            text = text[:8000] + "..."
            logger.warning("Text truncated to 8000 characters for embedding")

        logger.info(f"Generating embedding for {len(text)} characters")

        response = client.embeddings.create(model=settings.OPENAI_EMBED_MODEL, input=[text], timeout=30)

        embedding = response.data[0].embedding
        logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
        return embedding

    except Exception as e:
        logger.error(f"OpenAI embeddings API error: {e}")
        raise AIError(f"Failed to generate embedding: {e}")


def embed_query(query: str) -> List[float]:
    """
    Generate embedding for a search query.

    Args:
        query: Search query text

    Returns:
        List of embedding values
    """
    return generate_embedding(query)
