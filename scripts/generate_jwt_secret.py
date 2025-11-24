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
        length: 密钥长度(默认64位)
    
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
    print("JWT")
    print("=" * 70)
    print()
    
    # 生成3个不同长度的密钥供选择
    print("64(): ")
    print("-" * 70)
    secret_64 = generate_jwt_secret(64)
    print(secret_64)
    print()
    
    print("32(): ")
    print("-" * 70)
    secret_32 = generate_jwt_secret(32)
    print(secret_32)
    print()
    
    print(": ")
    print("-" * 70)
    print("1. (64)")
    print("2.  .env ")
    print("3.  JWT_SECRET= ")
    print("4. ")
    print("5. Save")
    print()
    print(": ")
    print(f"JWT_SECRET={secret_64}")
    print()
    print("=" * 70)
