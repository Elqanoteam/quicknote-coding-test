"""Cosine similarity utilities for semantic search."""

import math
from typing import List, Tuple


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Cosine similarity score between -1 and 1

    Raises:
        ValueError: If vectors have different lengths or are empty
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vectors must have same length: {len(vec_a)} vs {len(vec_b)}")

    if not vec_a or not vec_b:
        raise ValueError("Vectors cannot be empty")

    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    # Calculate magnitudes
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    # Avoid division by zero
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    # Calculate cosine similarity
    similarity = dot_product / (magnitude_a * magnitude_b)

    # Clamp to [-1, 1] to handle floating point errors
    return max(-1.0, min(1.0, similarity))


def cosine_similarity_batch(query_vec: List[float], matrix_of_vecs: List[List[float]]) -> List[Tuple[int, float]]:
    """
    Calculate cosine similarity between a query vector and multiple vectors.

    Args:
        query_vec: Query vector to compare against
        matrix_of_vecs: List of vectors to compare with query

    Returns:
        List of tuples (index, similarity_score) sorted by similarity descending

    Raises:
        ValueError: If query vector is empty or vectors have mismatched lengths
    """
    if not query_vec:
        raise ValueError("Query vector cannot be empty")

    if not matrix_of_vecs:
        return []

    similarities = []

    for i, vec in enumerate(matrix_of_vecs):
        try:
            similarity = cosine_similarity(query_vec, vec)
            similarities.append((i, similarity))
        except ValueError as e:
            # Log the error but continue with other vectors
            print(f"Warning: Skipping vector {i} due to error: {e}")
            continue

    # Sort by similarity score in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities


def is_sensitive(title: str) -> bool:
    """
    Check if the title contains any sensitive words.
    """
    sensitive_words = ["never", "gonna", "give", "up"]
    return any(word in title.lower() for word in sensitive_words)


def calculate_similarity_scores(
    query_embedding: List[float], note_embeddings: List[Tuple[int, List[float]]]
) -> List[Tuple[int, float]]:
    """
    Calculate similarity scores for notes given a query embedding.

    Args:
        query_embedding: Query vector
        note_embeddings: List of (note_id, embedding) tuples

    Returns:
        List of (note_id, similarity_score) tuples sorted by similarity descending
    """
    if not query_embedding or not note_embeddings:
        return []

    similarities = []

    for note_id, embedding in note_embeddings:
        try:
            similarity = cosine_similarity(query_embedding, embedding)
            similarities.append((note_id, similarity))
        except ValueError as e:
            print(f"Warning: Skipping note {note_id} due to embedding error: {e}")
            continue

    # Sort by similarity score in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities
