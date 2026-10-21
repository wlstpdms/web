import unittest
from http.cookies import SimpleCookie
from unittest.mock import patch

from fastapi import HTTPException, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.routers.kakao_auth import _set_kakao_state_cookie
from app.api.routers.user import login, signup
from app.api.routers.language import current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.user import LoginReq, SignUpReq


class CookieSettingsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        User.__table__.create(self.engine)
        self.db = Session(self.engine)
        self.db.add(User(email="cookie@example.invalid", password="test-password", name="Test"))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_login_cookie_for_production_and_local(self):
        for domain, secure in [("my-do.kro.kr", False), ("my-do.kro.kr", True), (None, False)]:
            with self.subTest(domain=domain, secure=secure), patch.object(
                settings, "COOKIE_DOMAIN", domain
            ), patch.object(settings, "COOKIE_SECURE", secure):
                response = Response()
                login(LoginReq(email="cookie@example.invalid", password="test-password"), response, self.db)
                cookie = SimpleCookie(response.headers["set-cookie"])["EN_AT"]
                self.assertEqual(cookie["domain"], domain or "")
                self.assertEqual(bool(cookie["secure"]), secure)
                self.assertTrue(cookie["httponly"])
                self.assertEqual(cookie["samesite"], "lax")
                self.assertEqual(cookie["path"], "/")
                self.assertTrue(cookie.value)

    def test_failed_login_does_not_issue_cookie(self):
        response = Response()
        with self.assertRaises(HTTPException) as raised:
            login(LoginReq(email="cookie@example.invalid", password="wrong"), response, self.db)
        self.assertEqual(raised.exception.status_code, 401)
        self.assertNotIn("set-cookie", response.headers)

    def test_signup_then_login_cookie_authenticates_the_created_user(self):
        signup(SignUpReq(email="new@example.invalid", password="new-password", name="New user"), self.db)
        response = Response()
        login(LoginReq(email="new@example.invalid", password="new-password"), response, self.db)
        token = SimpleCookie(response.headers["set-cookie"])["EN_AT"].value
        request = Request({"type": "http", "headers": [(b"cookie", f"EN_AT={token}".encode())]})
        self.assertEqual(current_user(request, self.db).email, "new@example.invalid")

    def test_duplicate_signup_is_rejected_without_breaking_existing_login(self):
        with self.assertRaises(HTTPException) as raised:
            signup(SignUpReq(email=" COOKIE@example.invalid ", password="other", name="Duplicate"), self.db)
        self.assertEqual(raised.exception.status_code, 400)
        response = Response()
        login(LoginReq(email="cookie@example.invalid", password="test-password"), response, self.db)
        self.assertIn("set-cookie", response.headers)

    def test_kakao_state_uses_same_cookie_scope(self):
        with patch.object(settings, "COOKIE_DOMAIN", "my-do.kro.kr"), patch.object(
            settings, "COOKIE_SECURE", False
        ):
            response = Response()
            _set_kakao_state_cookie(response, "test-state")
            cookie = SimpleCookie(response.headers["set-cookie"])["KAKAO_OAUTH_STATE"]
            self.assertEqual(cookie["domain"], "my-do.kro.kr")
            self.assertEqual(cookie["path"], "/")
            self.assertEqual(cookie["max-age"], "600")
            self.assertTrue(cookie["httponly"])
            self.assertFalse(cookie["secure"])


if __name__ == "__main__":
    unittest.main()
