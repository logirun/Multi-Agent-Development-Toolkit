"""
AegisFlow Authentication Module (src/auth.py)
==============================================

对齐并实现 docs/contracts/SPEC-0001-auth-contract.json 契约的标准用户鉴权业务服务。
提供基于 HMAC-SHA256 的紧凑型 JWT 令牌生成、恒定时间摘要验签与生命周期校验。
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional

# 演示环境默认签名盐值 (生产环境应通过环境变量注入)
SECRET_SALT = b"aegisflow_demo_signing_salt_key_2026"


class AuthService:
    """
    用户身份认证与 JWT 令牌生命周期管理服务。
    """

    def __init__(self, expires_in: int = 3600):
        """
        初始化鉴权服务。

        :param expires_in: 访问令牌有效生命周期 (秒)，默认 3600 秒 (1小时)
        """
        self.expires_in = expires_in

    def generate_token(self, username: str) -> str:
        """
        基于 HMAC-SHA256 签发标准三段式 JWT 令牌。

        :param username: 用户身份标识 (sub)
        :return: 编码并签署的 JWT 字符串 (header.payload.signature)
        """
        payload = {
            "sub": username,
            "iat": int(time.time()),
            "exp": int(time.time()) + self.expires_in
        }
        header = {"alg": "HS256", "typ": "JWT"}
        
        # 使用 URL 安全的 Base64 编码，并移除尾部填充符 '='
        encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
        encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        
        # 计算对称 HMAC-SHA256 签名
        signature_base = f"{encoded_header}.{encoded_payload}".encode()
        sig = hmac.new(SECRET_SALT, signature_base, hashlib.sha256).digest()
        encoded_sig = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
        
        return f"{encoded_header}.{encoded_payload}.{encoded_sig}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        校验 JWT 令牌完整性与有效性：
        1. 格式是否满足三段式。
        2. 使用 hmac.compare_digest 进行恒定时间比较，防范时序攻击 (Timing Attack)。
        3. 检查令牌是否已超过过期时间戳 (exp)。

        :param token: 待校验的 JWT 令牌字符串
        :return: 校验成功返回载荷字典，校验失败返回 None
        """
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, sig_b64 = parts
        signature_base = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(SECRET_SALT, signature_base, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
        
        # 恒定时间哈希比对防范侧信道攻击
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        try:
            payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
            payload = json.loads(payload_json)
            # 校验时效性
            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None

    def authenticate(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        执行用户登录凭证核验与令牌颁发。
        严格符合 SPEC-0001 契约规范中定义的出入参格式与字段长度约束。

        :param credentials: 包含 username 与 password 的凭据字典
        :return: 包含 access_token, token_type ('Bearer') 与 expires_in 的字典
        :raises ValueError: 当凭据不满足基本格式约束时抛出
        """
        username = credentials.get("username", "")
        password = credentials.get("password", "")

        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        # 验证通过后颁发 Token
        access_token = self.generate_token(username)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": self.expires_in
        }
