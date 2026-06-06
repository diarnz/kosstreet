from __future__ import annotations

from enum import StrEnum

from kostreet_ai.inference.prompts.base import BASE_PROMPT
from kostreet_ai.inference.prompts.citizen_upload import CITIZEN_UPLOAD_PROMPT
from kostreet_ai.inference.prompts.disambiguation import DISAMBIGUATION_PROMPT
from kostreet_ai.inference.prompts.street_view import STREET_VIEW_PROMPT
from kostreet_ai.schemas import IssueCategory

_DEFAULT_USER_TEXT = "Analyze this street-level photograph for civic infrastructure issues."


class ClassificationContext(StrEnum):
    street_audit = "street_audit"
    citizen_upload = "citizen_upload"


def build_system_prompt(context: ClassificationContext = ClassificationContext.citizen_upload) -> str:
    sections = [BASE_PROMPT, DISAMBIGUATION_PROMPT]
    if context == ClassificationContext.street_audit:
        sections.append(STREET_VIEW_PROMPT)
    else:
        sections.append(CITIZEN_UPLOAD_PROMPT)
    return "\n\n".join(sections)


def build_user_text(context: ClassificationContext = ClassificationContext.citizen_upload) -> str:
    return _DEFAULT_USER_TEXT


def build_second_pass_user_text(
    first_category: IssueCategory,
    first_confidence: float,
    alternatives: tuple[IssueCategory, ...],
) -> str:
    alt_labels = ", ".join(cat.value for cat in alternatives)
    return (
        f"You previously classified this image as {first_category.value} "
        f"with confidence {first_confidence:.2f}. "
        f"Re-examine ONLY whether it should instead be one of: {alt_labels}. "
        "Respond with the same JSON schema."
    )


# Alternatives offered during the focused second pass.
_SECOND_PASS_ALTERNATIVES: dict[IssueCategory, tuple[IssueCategory, ...]] = {
    IssueCategory.pothole: (
        IssueCategory.blocked_sidewalk,
        IssueCategory.garbage,
        IssueCategory.other,
    ),
    IssueCategory.garbage: (IssueCategory.blocked_sidewalk, IssueCategory.other),
    IssueCategory.blocked_sidewalk: (IssueCategory.pothole, IssueCategory.garbage),
    IssueCategory.damaged_sign: (IssueCategory.broken_streetlight, IssueCategory.other),
    IssueCategory.broken_streetlight: (IssueCategory.damaged_sign, IssueCategory.other),
    IssueCategory.other: (
        IssueCategory.garbage,
        IssueCategory.blocked_sidewalk,
        IssueCategory.damaged_sign,
        IssueCategory.broken_streetlight,
    ),
}


def second_pass_alternatives(category: IssueCategory) -> tuple[IssueCategory, ...]:
    return _SECOND_PASS_ALTERNATIVES.get(category, (IssueCategory.other,))
