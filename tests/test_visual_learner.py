"""
Unit tests for Hallwright v0.10.87 Autonomous Visual PC Learner (visual_learner.py).
Verifies:
- Micro-thumbnail capture with strict max_dim <= 192 and lightweight file size (<20KB).
- Automated perceptual feature extraction (luminance, dark mode, contrast, palette).
- Adaptive training on user positive demand (convention) vs negative rejection (anti-pattern).
- MCP tool dispatch for hallwright_learn_from_pc and legacy artisan_learn_from_pc.
"""

import os
import sys
import tempfile
import pytest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp")))

from visual_learner import VisualPCLearner
import server as mcp_server


@pytest.fixture
def temp_learner(tmp_path):
    learner = VisualPCLearner(workspace_root=str(tmp_path))
    return learner, tmp_path


def test_micro_snapshot_downscaling(temp_learner):
    learner, tmp_path = temp_learner
    # Create high-res test image (1200x800)
    img_path = str(tmp_path / "high_res_screen.png")
    img = Image.new("RGB", (1200, 800), color=(15, 23, 42))
    img.save(img_path)

    snapshot = learner.capture_micro_snapshot(source_image=img_path, max_dim=192)

    assert os.path.exists(snapshot["thumbnail_path"])
    assert snapshot["width"] <= 192
    assert snapshot["height"] <= 192
    # Ensure token conservation invariant: file size well under 20KB
    assert snapshot["bytes_size"] < 20480
    assert "average_luminance" in snapshot["features"]
    assert "dominant_colors" in snapshot["features"]
    assert snapshot["features"]["is_dark_mode"] is True


def test_train_from_pc_rejection(temp_learner):
    learner, tmp_path = temp_learner
    img_path = str(tmp_path / "medax_dull.png")
    # Dull gray image simulating generic site
    img = Image.new("RGB", (600, 400), color=(220, 220, 220))
    img.save(img_path)

    demand = "menga bunaqa sayt kerak emas bu loyihamiz qoshilgandan keyingi holat"
    result = learner.train_from_pc(user_demand=demand, source_image=img_path)

    assert result["status"] == "TRAINED"
    assert result["type"] == "anti_pattern"
    assert result["learned_rule"] == "AVOID_GENERIC_FLAT_CATALOGS"
    assert "REJECTED DESIGN PATTERN" in result["lesson"]

    profile = learner.get_learned_profile()
    assert profile["total_trainings"] >= 1
    assert "AVOID_GENERIC_FLAT_CATALOGS" in profile["banned_patterns"]


def test_train_from_pc_approval(temp_learner):
    learner, tmp_path = temp_learner
    img_path = str(tmp_path / "modern_dark.png")
    # Ultra-dark rich indigo image
    img = Image.new("RGB", (600, 400), color=(15, 23, 42))
    img.save(img_path)

    demand = "zamonaviy dark-mode va 3D spatial canvas bo'lsin"
    result = learner.train_from_pc(user_demand=demand, source_image=img_path)

    assert result["status"] == "TRAINED"
    assert result["type"] == "convention"
    assert result["learned_rule"] == "ENFORCE_USER_LEARNED_AESTHETICS"
    assert "LEARNED USER PREFERENCE" in result["lesson"]

    profile = learner.get_learned_profile()
    assert profile["preferred_theme"] == "dark"


def test_mcp_learn_from_pc_dispatch():
    import json
    req = {
        "jsonrpc": "2.0",
        "id": "test-learn-1",
        "method": "tools/call",
        "params": {
            "name": "hallwright_learn_from_pc",
            "arguments": {
                "demand": "faqat eng zamonaviy shisha effektlari va micro-animatsiyalar bo'lsin"
            }
        }
    }
    resp = mcp_server.dispatch_request(req)
    assert resp["id"] == "test-learn-1"
    assert "result" in resp
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "TRAINED"
    assert content["type"] == "convention"


def test_mcp_legacy_artisan_learn_from_pc_alias():
    import json
    req = {
        "jsonrpc": "2.0",
        "id": "test-learn-2",
        "method": "tools/call",
        "params": {
            "name": "artisan_learn_from_pc",
            "arguments": {
                "demand": "bunday oddiy oq fonli dizayn kerak emas"
            }
        }
    }
    resp = mcp_server.dispatch_request(req)
    assert resp["id"] == "test-learn-2"
    assert "result" in resp
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "TRAINED"
    assert content["type"] == "anti_pattern"

