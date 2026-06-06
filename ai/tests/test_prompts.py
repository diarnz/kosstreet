from __future__ import annotations

from kostreet_ai.inference.prompts import (
    ClassificationContext,
    build_second_pass_user_text,
    build_system_prompt,
    second_pass_alternatives,
)
from kostreet_ai.schemas import IssueCategory


def test_system_prompt_includes_disambiguation_for_all_contexts() -> None:
    for context in ClassificationContext:
        prompt = build_system_prompt(context)
        assert "Category disambiguation" in prompt
        assert "pothole" in prompt


def test_street_audit_prompt_includes_distance_hints() -> None:
    prompt = build_system_prompt(ClassificationContext.street_audit)
    assert "10–30 meters" in prompt
    assert "garbage" in prompt


def test_citizen_upload_prompt_includes_close_up_hint() -> None:
    prompt = build_system_prompt(ClassificationContext.citizen_upload)
    assert "close-up" in prompt


def test_second_pass_user_text_lists_alternatives() -> None:
    text = build_second_pass_user_text(IssueCategory.pothole, 0.82, second_pass_alternatives(IssueCategory.pothole))
    assert "pothole" in text
    assert "0.82" in text
    assert "blocked_sidewalk" in text
