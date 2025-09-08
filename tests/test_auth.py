import pytest
from fastapi.testclient import TestClient
from app.core.auth import AuthService

class TestAuth:
    """认证测试"""
    
    def test_register_user(self, client: TestClient, test_user_data):
        """测试用户注册"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user_data["email"]
        assert data["data"]["username"] == test_user_data["username"]
    
    def test_register_duplicate_email(self, client: TestClient, test_user_data):
        """测试重复邮箱注册"""
        # 先注册一个用户
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 尝试用相同邮箱注册
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"]
    
    def test_login_user(self, client: TestClient, test_user_data):
        """测试用户登录"""
        # 先注册用户
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 登录
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """测试无效凭据登录"""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect email or password" in data["detail"]
    
    def test_get_current_user(self, client: TestClient, test_user_data):
        """测试获取当前用户信息"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=test_user_data)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["data"]["access_token"]
        
        # 获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user_data["email"]
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """测试未授权获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403