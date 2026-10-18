import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from hallwright_studio import capture_visual_metrics, run_studio_critique, elevate_html_to_world_class


def test_studio_critique_on_beginner_site(tmp_path):
    beginner_html = tmp_path / "beginner.html"
    beginner_html.write_text("""<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Welcome to our test site</h1>
    <p>We provide the best services.</p>
    <button>Click here</button>
</body>
</html>
""", encoding="utf-8")

    metrics = capture_visual_metrics(str(beginner_html))
    critique = run_studio_critique(str(beginner_html), metrics)

    # Initial beginner page should be flagged by Elena and Diana
    assert critique["composite_score"] < 80
    assert len(critique["elena"]["critiques"]) > 0
    assert len(critique["diana"]["critiques"]) > 0
    assert "Diagnosed Mediocrity" in critique["self_critique"]["why_is_this_mediocre"] or "entry-level" in critique["self_critique"]["why_is_this_mediocre"]


def test_studio_elevation_enhancement(tmp_path):
    site_html = tmp_path / "elevate_test.html"
    site_html.write_text("""<!DOCTYPE html>
<html>
<head><title>Unpolished</title></head>
<body>
    <h1>Welcome to the product</h1>
    <button>Click here</button>
    <a href="https://example.com" target="_blank">Learn more</a>
</body>
</html>
""", encoding="utf-8")

    # Run elevation
    elevated_content = elevate_html_to_world_class(str(site_html))
    
    # Assert world-class features injected
    assert "fonts.googleapis.com" in elevated_content
    assert "hallwright-studio-elevation" in elevated_content
    assert "backdrop-filter" in elevated_content
    assert "rel=\"noopener noreferrer\"" in elevated_content
    assert "Discover the Future of the product" in elevated_content
    assert "Get Instant Access" in elevated_content
    assert "Explore The Architecture" in elevated_content

    # Re-audit elevated page
    new_metrics = capture_visual_metrics(str(site_html))
    new_critique = run_studio_critique(str(site_html), new_metrics)
    assert new_critique["composite_score"] >= 80
