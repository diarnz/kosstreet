"""Category disambiguation rules and weak-category detection hints."""

DISAMBIGUATION_PROMPT = """Category disambiguation — apply these rules when categories could overlap:
- Waste, bags, bottles, bins, or scattered debris on ANY surface → garbage (not blocked_sidewalk)
- Crack or hole in the ROAD LANE or vehicle roadway → pothole (not blocked_sidewalk)
- Crack, obstacle, or obstruction on SIDEWALK or pedestrian path ONLY → blocked_sidewalk (not pothole)
- Bent, fallen, missing, or graffitied SIGN BOARD or traffic sign → damaged_sign (not broken_streetlight)
- Damaged LAMP, light fixture, or lighting pole → broken_streetlight (not damaged_sign)
- Flooding, standing water, graffiti, drainage failure, vandalism, or uncategorized civic harm → other with is_civic_issue true (not a clean image)
- Clean street with no actionable issue → other with is_civic_issue false

Look harder for these often-missed issues:
- garbage: single plastic bottles, cigarette packs, scattered papers, overflowing bins, construction debris piles, tire dumps
- other: standing water on the road, wall graffiti, broken curb without a pothole, exposed cables, fallen tree branches
- damaged_sign: rust, missing sign face, bent post, graffiti on the sign panel (not the lamp on the pole)"""
