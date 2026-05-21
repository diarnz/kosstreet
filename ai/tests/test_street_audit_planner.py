from kostreet_ai.street_audit.planner import build_heading_plan


def test_build_heading_plan_combines_headings_and_pitches() -> None:
    frames = build_heading_plan(42.6629, 21.1655, headings=(0, 90), pitches=(-10, 0))

    assert len(frames) == 4
    assert frames[0].heading == 0
    assert frames[-1].pitch == 0

