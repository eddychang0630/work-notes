"""Redfish FirmwareInventory -> CSV（對應筆記第 8 章）。

環境變數：BMC_BASE_URL、BMC_USER、BMC_PASSWORD，選用 BMC_CA_BUNDLE（CA 憑證路徑）。
只做唯讀 GET，以及建立／刪除自己的 Session。
"""
import csv, os, sys
import requests


class Redfish:
    def __init__(self, base, user, password, verify=True, timeout=(5, 20)):
        self.base, self.timeout = base.rstrip("/"), timeout
        self.http = requests.Session()
        self.http.verify = verify
        self.session_uri = None
        self._login(user, password)

    def _login(self, user, password):
        root = self.http.get(self.base + "/redfish/v1/", timeout=self.timeout)
        root.raise_for_status()
        # Sessions 位置以 Service Root 的連結為準，不寫死
        sessions = (root.json().get("Links", {}).get("Sessions", {})
                    .get("@odata.id", "/redfish/v1/SessionService/Sessions"))
        r = self.http.post(self.base + sessions,
                           json={"UserName": user, "Password": password},
                           timeout=self.timeout)
        r.raise_for_status()
        self.http.headers["X-Auth-Token"] = r.headers["X-Auth-Token"]
        self.session_uri = r.headers.get("Location")

    def get(self, uri):
        r = self.http.get(self.base + uri, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def close(self):
        if self.session_uri:
            uri = self.session_uri
            if uri.startswith("http"):                 # 有些實作回傳完整 URL
                uri = "/" + uri.split("/", 3)[3]
            try:
                self.http.delete(self.base + uri, timeout=self.timeout)
            except requests.RequestException:
                pass                                    # 登出失敗不影響結果

    def __enter__(self): return self
    def __exit__(self, *exc): self.close()


def firmware_rows(rf):
    update = rf.get("/redfish/v1/UpdateService")
    link = (update.get("FirmwareInventory") or {}).get("@odata.id")
    if not link:
        print("此平台的 UpdateService 沒有 FirmwareInventory 連結", file=sys.stderr)
        return
    for member in rf.get(link).get("Members", []):
        try:
            item = rf.get(member["@odata.id"])
        except requests.HTTPError as e:
            yield {"Id": member["@odata.id"], "Error": str(e.response.status_code)}
            continue
        yield {
            "Id": item.get("Id"),
            "Name": item.get("Name"),
            "Version": item.get("Version"),              # 可能為 None
            "Updateable": item.get("Updateable"),
            "Health": (item.get("Status") or {}).get("Health"),
        }


if __name__ == "__main__":
    verify = os.environ.get("BMC_CA_BUNDLE", True)
    with Redfish(os.environ["BMC_BASE_URL"], os.environ["BMC_USER"],
                 os.environ["BMC_PASSWORD"], verify=verify) as rf:
        rows = list(firmware_rows(rf))
    fields = ["Id", "Name", "Version", "Updateable", "Health", "Error"]
    with open("firmware_inventory.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"已輸出 {len(rows)} 筆")
