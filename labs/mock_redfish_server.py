"""教學用模擬 Redfish 伺服器（對應筆記第 8、16 章）。

- 只使用 Python 標準函式庫；明文 HTTP、預設只聽 127.0.0.1，**僅供本機練習**。
- 資料為教學自訂，不代表任何真實 BMC／SMM 的回應。
- 帳號固定為 labuser；密碼由環境變數 MOCK_PASSWORD 指定（不寫在程式裡）。

用法：
    export MOCK_PASSWORD='choose-a-lab-password'
    python3 labs/mock_redfish_server.py [--port 8000] [--fail-session]
"""
import argparse
import base64
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USER = "labuser"
PASSWORD = os.environ.get("MOCK_PASSWORD")
SESSIONS = {}          # session id -> token
FAIL_SESSION = False

FW = {
    "BMC-Primary": {"Name": "BMC (Primary)", "Version": "3.10", "Updateable": True},
    "UEFI":        {"Name": "UEFI", "Version": "2.41", "Updateable": True},
    "PCS1":        {"Name": "Power Supply 1 Firmware", "Version": "00.51", "Updateable": True},
    "PCS2":        {"Name": "Power Supply 2 Firmware", "Version": "00.51", "Updateable": True},
    "PCS3":        {"Name": "Power Supply 3 Firmware", "Version": None, "Updateable": False},   # 故意：版本為 null
    "PCS4":        None,                                                                       # 故意：GET 回 500
}


def resources():
    root = "/redfish/v1"
    res = {
        root + "/": {
            "@odata.id": root + "/", "Name": "Mock Service Root", "RedfishVersion": "1.15.0",
            "Chassis": {"@odata.id": root + "/Chassis"},
            "Managers": {"@odata.id": root + "/Managers"},
            "UpdateService": {"@odata.id": root + "/UpdateService"},
            "SessionService": {"@odata.id": root + "/SessionService"},
            "Links": {"Sessions": {"@odata.id": root + "/SessionService/Sessions"}},
        },
        root + "/UpdateService": {
            "@odata.id": root + "/UpdateService", "Name": "Update Service", "ServiceEnabled": True,
            "FirmwareInventory": {"@odata.id": root + "/UpdateService/FirmwareInventory"},
        },
        root + "/UpdateService/FirmwareInventory": {
            "@odata.id": root + "/UpdateService/FirmwareInventory",
            "Name": "Firmware Inventory Collection", "Members@odata.count": len(FW),
            "Members": [{"@odata.id": f"{root}/UpdateService/FirmwareInventory/{k}"} for k in FW],
        },
        root + "/Chassis": {
            "@odata.id": root + "/Chassis", "Name": "Chassis Collection", "Members@odata.count": 1,
            "Members": [{"@odata.id": root + "/Chassis/Enclosure"}],
        },
        root + "/Chassis/Enclosure": {
            "@odata.id": root + "/Chassis/Enclosure", "Id": "Enclosure", "Name": "Mock Enclosure",
            "Status": {"State": "Enabled", "Health": "OK"},
            "Power": {"@odata.id": root + "/Chassis/Enclosure/Power"},
        },
        root + "/Chassis/Enclosure/Power": {
            "@odata.id": root + "/Chassis/Enclosure/Power", "Name": "Power",
            "PowerSupplies": [
                {"MemberId": "1", "Name": "PSU1", "FirmwareVersion": "00.51", "PowerCapacityWatts": 1800,
                 "LineInputVoltage": 230, "PowerInputWatts": 412, "PowerOutputWatts": 388,
                 "Status": {"State": "Enabled", "Health": "OK"}},
                {"MemberId": "2", "Name": "PSU2", "FirmwareVersion": "00.51", "PowerCapacityWatts": 1800,
                 "LineInputVoltage": 229, "PowerInputWatts": 405, "PowerOutputWatts": 381,
                 "Status": {"State": "Enabled", "Health": "OK"}},
                {"MemberId": "3", "Name": "PSU3", "FirmwareVersion": None, "PowerCapacityWatts": 1800,
                 "LineInputVoltage": None, "PowerInputWatts": None, "PowerOutputWatts": None,
                 "Status": {"State": "Enabled", "Health": "Warning"}},
                {"MemberId": "4", "Name": "PSU4", "Status": {"State": "Absent", "Health": None}},
            ],
        },
        root + "/Managers": {
            "@odata.id": root + "/Managers", "Name": "Manager Collection", "Members@odata.count": 1,
            "Members": [{"@odata.id": root + "/Managers/SMM"}],
        },
        root + "/Managers/SMM": {
            "@odata.id": root + "/Managers/SMM", "Id": "SMM", "Name": "Mock Enclosure Manager",
            "ManagerType": "EnclosureManager", "FirmwareVersion": "1.00",
        },
        root + "/SessionService": {
            "@odata.id": root + "/SessionService", "Name": "Session Service", "SessionTimeout": 300,
            "Sessions": {"@odata.id": root + "/SessionService/Sessions"},
        },
    }
    for key, item in FW.items():
        if item is not None:
            uri = f"{root}/UpdateService/FirmwareInventory/{key}"
            res[uri] = {"@odata.id": uri, "Id": key, **item, "Status": {"State": "Enabled", "Health": "OK"}}
    return res


class Handler(BaseHTTPRequestHandler):
    server_version = "MockRedfish/1.0"

    def _send(self, code, body=None, headers=None):
        data = json.dumps(body, indent=2).encode() if body is not None else b""
        self.send_response(code)
        if data:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _error(self, code, message):
        self._send(code, {"error": {"code": f"Base.1.0.Http{code}", "message": message}},
                   {"WWW-Authenticate": 'Basic realm="mock"'} if code == 401 else None)

    def _authed(self):
        token = self.headers.get("X-Auth-Token")
        if token and token in SESSIONS.values():
            return True
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Basic "):
            try:
                user, _, pw = base64.b64decode(auth[6:]).decode().partition(":")
            except Exception:
                return False
            return secrets.compare_digest(user, USER) and secrets.compare_digest(pw, PASSWORD)
        return False

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/redfish/v1", "/redfish/v1/"):
            return self._send(200, resources()["/redfish/v1/"])      # Service Root 免認證
        if not self._authed():
            return self._error(401, "Authentication required")
        path = path.rstrip("/")
        if path.endswith("/FirmwareInventory/PCS4"):
            return self._error(500, "Simulated internal error")
        res = resources().get(path)
        if res is None:
            return self._error(404, f"Resource {path} not found")
        self._send(200, res)

    def do_POST(self):
        if self.path.rstrip("/") != "/redfish/v1/SessionService/Sessions":
            return self._error(405, "POST not allowed here")
        if FAIL_SESSION:
            return self._send(503, {"error": {"message": "Session limit reached"}}, {"Retry-After": "5"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self._error(400, "Malformed JSON")
        if not (secrets.compare_digest(str(body.get("UserName", "")), USER)
                and secrets.compare_digest(str(body.get("Password", "")), PASSWORD)):
            return self._error(401, "Invalid credentials")
        sid, token = str(len(SESSIONS) + 1), secrets.token_hex(16)
        SESSIONS[sid] = token
        uri = f"/redfish/v1/SessionService/Sessions/{sid}"
        print(f"[session] created {sid}")
        self._send(201, {"@odata.id": uri, "Id": sid, "UserName": USER},
                   {"X-Auth-Token": token, "Location": uri})

    def do_DELETE(self):
        if not self._authed():
            return self._error(401, "Authentication required")
        sid = self.path.rstrip("/").rsplit("/", 1)[-1]
        if self.path.startswith("/redfish/v1/SessionService/Sessions/") and sid in SESSIONS:
            del SESSIONS[sid]
            print(f"[session] deleted {sid}")
            return self._send(204)
        self._error(404, "Session not found")

    def do_PATCH(self):
        self._error(405, "This mock is read-only")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="教學用模擬 Redfish 伺服器（僅本機）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--fail-session", action="store_true", help="建立 Session 時一律回 503")
    args = ap.parse_args()
    if not PASSWORD:
        raise SystemExit("請先設定環境變數 MOCK_PASSWORD（練習用密碼）")
    FAIL_SESSION = args.fail_session
    print(f"Mock Redfish on http://{args.host}:{args.port}/redfish/v1/  (user: {USER})")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
