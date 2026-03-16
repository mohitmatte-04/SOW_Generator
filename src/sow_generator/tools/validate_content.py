"""Tool to validate and score SOW content quality."""

import logging
from typing import Any

from ..config import VALIDATION_QUALITY_THRESHOLD, VALIDATION_WEIGHTS

logger = logging.getLogger(__name__)


async def validate_content(
    dimension_scores: dict[str, int],
    section_feedback: list[dict[str, Any]] | None = None,
    summary: str = "",
) -> dict[str, Any]:
    """Validates SOW content quality by computing a weighted overall score.

    Accepts per-dimension scores (0–100) from the LLM evaluation and computes
    a weighted overall quality score. Compares against the configurable threshold
    to determine if content is approved or needs improvement.

    Args:
        dimension_scores: Dictionary mapping dimension names to scores (0–100).
            Expected keys: content_quality, grammar, sentence_structure,
            clarity, coherence.
        section_feedback: Optional list of section-level feedback dicts, each
            containing: section, score, issues, suggestions, original_text,
            suggested_text.
        summary: Overall quality summary from the LLM evaluation.

    Returns:
        Dictionary with validation status, scores, feedback, and threshold.
        Example: {"status": "approved", "overall_score": 82, ...}
    """
    try:
        # Validate dimension scores
        validated_scores: dict[str, dict[str, float | int]] = {}
        weighted_total = 0.0

        for dimension, weight in VALIDATION_WEIGHTS.items():
            score = dimension_scores.get(dimension, 0)

            # Clamp score to valid range
            score = max(0, min(100, int(score)))

            validated_scores[dimension] = {
                "score": score,
                "weight": weight,
            }
            weighted_total += score * weight

        overall_score = round(weighted_total, 1)

        # Determine approval status
        threshold = VALIDATION_QUALITY_THRESHOLD
        status = "approved" if overall_score >= threshold else "needs_improvement"

        # Build result
        result: dict[str, Any] = {
            "status": status,
            "overall_score": overall_score,
            "threshold": threshold,
            "dimension_scores": validated_scores,
            "section_feedback": section_feedback or [],
            "summary": summary,
        }

        logger.info(
            "Content validation complete: score=%.1f, threshold=%d, status=%s",
            overall_score,
            threshold,
            status,
        )

        if status == "needs_improvement" and section_feedback:
            logger.info(
                "Sections needing improvement: %s",
                [fb.get("section", "unknown") for fb in section_feedback],
            )

        for dimension, data in validated_scores.items():
            logger.debug(
                "  %s: score=%d (weight=%.0f%%)",
                dimension,
                data["score"],
                data["weight"] * 100,
            )

        return result

    except Exception as e:
        logger.error("Content validation failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "error": str(e),
        }
