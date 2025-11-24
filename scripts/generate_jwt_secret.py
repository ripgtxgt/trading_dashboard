#!/usr/bin/env python3
"""
JWT密钥生成工具
用于生成安全的随机JWT密钥
"""
import secrets
import string

def generate_jwt_secret(length=64):
    """
    生成安全的JWT密钥
    
    Args:
        length: 密钥长度（默认64位）
    
    Returns:
        随机生成的JWT密钥字符串
    """
    # 使用字母、数字和特殊字符
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # 使用secrets模块生成加密安全的随机字符串
    secret = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return secret

if __name__ == "__main__":
    print("=" * 70)
    print("JWT密钥生成工具")
    print("=" * 70)
    print()
    
    # 生成3个不同长度的密钥供选择
    print("推荐使用64位密钥（最安全）：")
    print("-" * 70)
    secret_64 = generate_jwt_secret(64)
    print(secret_64)
    print()
    
    print("32位密钥（适中）：")
    print("-" * 70)
    secret_32 = generate_jwt_secret(32)
    print(secret_32)
    print()
    
    print("使用方法：")
    print("-" * 70)
    print("1. 复制上面的密钥（推荐64位）")
    print("2. 打开 .env 文件")
    print("3. 找到 JWT_SECRET= 这一行")
    print("4. 将密钥粘贴到等号后面")
    print("5. 保存文件")
    print()
    print("示例：")
    print(f"JWT_SECRET={secret_64}")
    print()
    print("=" * 70)
