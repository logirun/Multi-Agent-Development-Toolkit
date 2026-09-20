"""
Unit tests for AuthService (tests/test_auth.py)
================================================

对齐 docs/contracts/SPEC-0001-auth-contract.json 的业务逻辑测试：
- 正常身份凭据登录与 JWT 令牌签发及解析验证。
- 非法入参长度校验与异常抛出。
- 篡改签名或载荷时恒定时间比对失败验证。
"""

import unittest
from src.auth import AuthService


class TestAuthService(unittest.TestCase):
    """
    AuthService 单元测试用例集。
    """

    def setUp(self):
        """
        初始化测试用 AuthService 实例，设定较短的 10 秒有效期。
        """
        self.auth = AuthService(expires_in=10)

    def test_authenticate_success(self):
        """
        测试合法凭据登录成功，签发 Bearer 令牌并能正确解码出 sub 主题。
        """
        res = self.auth.authenticate({"username": "alice", "password": "SecurePassword123!"})
        self.assertIn("access_token", res)
        self.assertEqual(res["token_type"], "Bearer")
        self.assertEqual(res["expires_in"], 10)

        # 校验生成的 Token 可正常解包并还原用户信息
        payload = self.auth.verify_token(res["access_token"])
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "alice")

    def test_authenticate_validation_failure(self):
        """
        测试用户名或密码长度不足时抛出 ValueError。
        """
        with self.assertRaises(ValueError):
            self.auth.authenticate({"username": "al", "password": "123"})

    def test_tampered_token_fails(self):
        """
        测试载荷或签名被篡改时，verify_token 必须准确返回 None。
        """
        res = self.auth.authenticate({"username": "bob", "password": "SuperSecretPassword999"})
        token = res["access_token"]
        
        # 恶意篡改载荷段
        parts = token.split(".")
        tampered_token = f"{parts[0]}.{parts[1]}xyz.{parts[2]}"
        self.assertIsNone(self.auth.verify_token(tampered_token))


if __name__ == "__main__":
    unittest.main()
