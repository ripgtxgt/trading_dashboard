@echo off
REM Trading Dashboard 一键部署启动器
REM 版本: 1.0

title Trading Dashboard - 一键部署

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║       Trading Dashboard 一键部署程序                      ║
echo ║       Version 1.0 for Windows Server 2022                 ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] 需要管理员权限运行此程序
    echo [!] 正在请求管理员权限...
    echo.
    
    REM 请求管理员权限并重新运行
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [OK] 管理员权限检查通过
echo.

REM 切换到脚本目录
cd /d "%~dp0"

REM 运行PowerShell部署脚本
echo [*] 正在启动部署脚本...
echo.

powershell -ExecutionPolicy Bypass -File "deploy.ps1"

if %errorLevel% equ 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                                                            ║
    echo ║                  部署完成！                                ║
    echo ║                                                            ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                                                            ║
    echo ║              部署失败，请查看错误信息                      ║
    echo ║                                                            ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
)

pause
