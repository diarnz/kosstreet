from __future__ import annotations

from kostreet_ai.integrations.street_view import (
    GoogleStreetViewClient,
    StreetViewFrameRequest,
    is_no_imagery_placeholder,
)


def test_is_no_imagery_placeholder_detects_tiny_payload() -> None:
    assert is_no_imagery_placeholder(b"x" * 25_000) is False
    assert is_no_imagery_placeholder(b"tiny") is True


def test_fetch_frame_uses_snapped_coordinates(monkeypatch) -> None:
    captured: dict = {}

    class FakeResponse:
        headers = {"content-type": "image/jpeg"}
        content = b"\xff\xd8" + b"x" * 30_000

        @staticmethod
        def raise_for_status() -> None:
            return None

    def fake_get(url, params=None, timeout=30.0):
        captured["url"] = url
        captured["params"] = params
        return FakeResponse()

    monkeypatch.setattr("kostreet_ai.integrations.street_view.httpx.get", fake_get)
    monkeypatch.setattr(
        "kostreet_ai.integrations.street_view.snap_to_nearest_panorama",
        lambda api_key, lat, lng: (42.6600, 21.1550),
    )

    client = GoogleStreetViewClient(api_key="test-key", size=640)
    frame = client.fetch_frame(StreetViewFrameRequest(latitude=42.6596, longitude=21.1545, heading=90))

    assert frame.snapped is True
    assert frame.latitude == 42.6600
    assert captured["params"]["heading"] == 90
    assert captured["params"]["location"] == "42.66,21.155"
