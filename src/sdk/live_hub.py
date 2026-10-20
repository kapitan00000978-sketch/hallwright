"""
Hallwright Live Mesh Hub & Real-Time SSE Server.
Part of Pillar III: Sub-Agent Mesh & Autonomous Intelligence Architecture.

Provides:
- Zero-dependency HTTP server serving the 3D Spatial Canvas HUD
- Real-time Server-Sent Events (SSE) stream bridging AgentMesh events to browser
- REST endpoints for live Swarm dispatch, Gatekeeper audits, and Web-Healing
"""

import os
import sys
import json
import time
import queue
import socket
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("hallwright.live_hub")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESIGN_DIR = os.path.join(ROOT_DIR, "src", "libraries", "design")

try:
    from agent_mesh import AgentMesh, AgentMessage
except ImportError:
    try:
        from src.sdk.agent_mesh import AgentMesh, AgentMessage
    except ImportError:
        AgentMesh = None
        AgentMessage = None


class LiveHubRegistry:
    """Manages active SSE client streams and distributes AgentMesh events."""
    def __init__(self):
        self._clients: List[queue.Queue] = []
        self._lock = threading.Lock()
        self.mesh: Optional[Any] = None

    def register_client(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=100)
        with self._lock:
            self._clients.append(q)
        return q

    def unregister_client(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)

    def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        with self._lock:
            dead_clients = []
            for q in self._clients:
                try:
                    q.put_nowait(payload)
                except queue.Full:
                    dead_clients.append(q)
            for d in dead_clients:
                if d in self._clients:
                    self._clients.remove(d)

    def connect_agent_mesh(self, mesh: Any) -> None:
        self.mesh = mesh
        mesh.subscribe("*", self._on_mesh_message)

    def _on_mesh_message(self, message: Any) -> None:
        msg_dict = message.to_dict() if hasattr(message, "to_dict") else vars(message)
        self.broadcast("agent_event", msg_dict)


hub_registry = LiveHubRegistry()


class LiveHubRequestHandler(BaseHTTPRequestHandler):
    """HTTP and SSE Request Handler for Hallwright 3D Spatial HUD."""

    def log_message(self, format_str: str, *args: Any) -> None:
        # Suppress noisy HTTP access logs in terminal
        pass

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path in ("/", "/index.html", "/dashboard_3d.html"):
            self._serve_file(os.path.join(DESIGN_DIR, "dashboard_3d.html"), "text/html")
        elif path == "/spatial_3d.js":
            self._serve_file(os.path.join(DESIGN_DIR, "spatial_3d.js"), "application/javascript")
        elif path == "/liquid_glass.css":
            self._serve_file(os.path.join(DESIGN_DIR, "liquid_glass.css"), "text/css")
        elif path == "/api/stream":
            self._handle_sse_stream()
        elif path == "/api/telemetry":
            self._handle_telemetry()
        elif path == "/api/immune":
            self._handle_immune_system()
        elif path == "/api/status":
            self._send_json({"status": "ONLINE", "server": "Hallwright Live Hub v2.0"})
        else:
            self.send_error(404, "Asset Not Found")

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

        if self.path == "/api/swarm":
            self._handle_swarm_dispatch(data)
        elif self.path == "/api/audit":
            self._handle_audit_dispatch()
        elif self.path == "/api/heal":
            self._handle_heal_dispatch(data)
        elif self.path == "/api/evolve":
            self._handle_evolve_dispatch(data)
        elif self.path == "/api/compress":
            self._handle_compress_dispatch(data)
        else:
            self.send_error(404, "Endpoint Not Found")

    def _serve_file(self, file_path: str, content_type: str) -> None:
        if not os.path.exists(file_path):
            self.send_error(404, "File Not Found")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except OSError as file_err:
            logger.debug("Failed serving %s: %s", file_path, file_err)
            self.send_error(500, "Internal Server Error")

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _handle_sse_stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        client_queue = hub_registry.register_client()
        # Send initial connection handshake
        init_event = f"event: connected\ndata: {json.dumps({'time': datetime.now(timezone.utc).isoformat(), 'status': 'READY'})}\n\n"
        try:
            self.wfile.write(init_event.encode("utf-8"))
            self.wfile.flush()
        except (OSError, BrokenPipeError):
            hub_registry.unregister_client(client_queue)
            return

        try:
            while True:
                try:
                    msg = client_queue.get(timeout=15.0)
                    self.wfile.write(msg.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    # Heartbeat comment to keep connection alive
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
        except (OSError, BrokenPipeError):
            logger.debug("SSE client disconnected")
        finally:
            hub_registry.unregister_client(client_queue)

    def _handle_telemetry(self) -> None:
        sys.path.insert(0, os.path.join(ROOT_DIR, "cli"))
        try:
            import dashboard
            telemetry = dashboard.get_telemetry()
        except Exception as tel_err:
            telemetry = {"status": "ACTIVE", "gatekeeper_score": 100, "error": str(tel_err)}
        self._send_json(telemetry)

    def _handle_swarm_dispatch(self, data: Dict[str, Any]) -> None:
        task = data.get("task", "Live Swarm Mesh Collaborative Execution")
        hub_registry.broadcast("swarm_start", {"task": task, "status": "STARTING"})
        try:
            from swarm import dispatch_swarm_mesh
            result = dispatch_swarm_mesh(task=task)
            hub_registry.broadcast("swarm_complete", result)
            self._send_json(result)
        except Exception as swarm_err:
            err_msg = {"status": "ERROR", "message": str(swarm_err)}
            hub_registry.broadcast("swarm_error", err_msg)
            self._send_json(err_msg, status=500)

    def _handle_audit_dispatch(self) -> None:
        hub_registry.broadcast("audit_start", {"status": "AUDITING"})
        try:
            sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
            from detector import scan_project
            result = scan_project(".", staged_only=False)
            audit_report = {
                "score": result.get("score", 100),
                "defects_count": len(result.get("findings", [])),
                "scanned_files": result.get("scanned_files", 0),
                "passed": result.get("score", 100) >= 85
            }
            hub_registry.broadcast("audit_complete", audit_report)
            self._send_json(audit_report)
        except Exception as audit_err:
            err_msg = {"status": "ERROR", "message": str(audit_err)}
            self._send_json(err_msg, status=500)

    def _handle_heal_dispatch(self, data: Dict[str, Any]) -> None:
        error_text = data.get("error", "Simulated defect resolution")
        hub_registry.broadcast("heal_start", {"error": error_text})
        try:
            from web_healer import AutonomousWebHealer
            healer = AutonomousWebHealer(workspace_root=ROOT_DIR)
            report = healer.heal_error(error_traceback=error_text)
            hub_registry.broadcast("heal_complete", report)
            self._send_json(report)
        except Exception as heal_err:
            err_msg = {"status": "ERROR", "message": str(heal_err)}
            self._send_json(err_msg, status=500)

    def _handle_immune_system(self) -> None:
        immune_path = os.path.join(ROOT_DIR, ".hallwright", "immune_system.json")
        if os.path.exists(immune_path):
            try:
                with open(immune_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self._send_json(state)
                return
            except Exception as read_err:
                logger.debug("Failed reading immune system: %s", read_err)
        self._send_json({"generation": 6, "immunity_score": 98, "vaccines": []})

    def _handle_evolve_dispatch(self, data: Dict[str, Any]) -> None:
        defect = data.get("defect", "Sample defect for autonomous evolution")
        try:
            from evolution import evolve_sync
            res = evolve_sync(defect)
            self._send_json(res)
        except Exception as evo_err:
            self._send_json({"status": "ERROR", "message": str(evo_err)}, status=500)

    def _handle_compress_dispatch(self, data: Dict[str, Any]) -> None:
        target = data.get("path", ".")
        try:
            from compressor import TokenCompressor
            compressor = TokenCompressor()
            stats_list = compressor.compress_directory(target, in_place=False)
            total_saved = sum(s.tokens_saved for s in stats_list)
            self._send_json({"status": "SUCCESS", "files_compressed": len(stats_list), "tokens_saved": total_saved})
        except Exception as comp_err:
            self._send_json({"status": "ERROR", "message": str(comp_err)}, status=500)


def find_free_port(starting_port: int = 8765, max_attempts: int = 20) -> int:
    """Finds an open TCP port starting from starting_port."""
    for port in range(starting_port, starting_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return starting_port


class LiveHubServer:
    """Zero-dependency background HTTP & SSE server."""
    def __init__(self, port: int = 8765):
        self.port = find_free_port(port)
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running = False

    def start(self, background: bool = True) -> str:
        # Connect shared AgentMesh to registry if available
        if AgentMesh:
            try:
                mesh = AgentMesh(workspace_root=ROOT_DIR)
                hub_registry.connect_agent_mesh(mesh)
            except Exception as mesh_err:
                logger.debug("LiveHub could not attach to AgentMesh: %s", mesh_err)

        self.server = HTTPServer(("127.0.0.1", self.port), LiveHubRequestHandler)
        self._is_running = True
        url = f"http://127.0.0.1:{self.port}"

        if background:
            self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self._thread.start()
            logger.info("Live Hub listening in background on %s", url)
        else:
            logger.info("Live Hub listening on %s", url)
            self.server.serve_forever()

        return url

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self._is_running = False


if __name__ == "__main__":
    hub = LiveHubServer()
    server_url = hub.start(background=False)
