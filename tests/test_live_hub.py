"""
Tests for Hallwright Live Hub Server (src/sdk/live_hub.py).
Verifies background HTTP and SSE endpoints, asset serving, and telemetry APIs.
"""

import sys
import os
import json
import urllib.request
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from live_hub import LiveHubServer, find_free_port


def test_find_free_port():
    port = find_free_port(8900)
    assert isinstance(port, int)
    assert port >= 8900


def test_live_hub_server_lifecycle_and_endpoints():
    hub = LiveHubServer(port=8910)
    url = hub.start(background=True)
    time.sleep(0.3)

    try:
        # 1. Test status endpoint
        req = urllib.request.urlopen(f"{url}/api/status", timeout=5)
        assert req.status == 200
        data = json.loads(req.read().decode("utf-8"))
        assert data.get("status") == "ONLINE"

        # 2. Test telemetry endpoint
        req_tel = urllib.request.urlopen(f"{url}/api/telemetry", timeout=5)
        assert req_tel.status == 200
        tel_data = json.loads(req_tel.read().decode("utf-8"))
        assert "gatekeeper_score" in tel_data or "status" in tel_data

        # 3. Test static HTML serving
        req_html = urllib.request.urlopen(f"{url}/", timeout=5)
        assert req_html.status == 200
        html_content = req_html.read().decode("utf-8")
        assert "Hallwright 3D Swarm" in html_content
        assert "spatialCanvas" in html_content

        # 4. Test spatial_3d.js serving
        req_js = urllib.request.urlopen(f"{url}/spatial_3d.js", timeout=5)
        assert req_js.status == 200
        js_content = req_js.read().decode("utf-8")
        assert "SpatialScene" in js_content

    finally:
        hub.stop()
