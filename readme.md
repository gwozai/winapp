# MinIO 文件管理器

MinIO 文件管理器是一个基于 PyQt5 开发的跨平台桌面应用程序，用于管理 MinIO 对象存储服务。它提供了直观的图形界面，支持文件上传、下载、分享等功能，并能生成便捷的 PowerShell 命令。

## 主要功能

### 1. 文件管理
- **文件浏览**
  - 列表显示所有文件
  - 显示文件大小、修改日期和类型
  - 支持文件搜索和过滤
  - 按文件类型分类（文本、图片、压缩包等）

- **文件操作**
  - 文件上传（支持进度显示）
  - 文件下载
  - 新建文件夹
  - 文件重命名
  - 文件删除
  - 文件预览
  - 文件分享（生成临时链接）

- **批量操作**
  - 多文件选择
  - 批量上传
  - 全选/取消全选

### 2. 命令生成
- **文件选择**
  - 支持多文件选择（复选框）
  - 文件过滤和搜索
  - 文件类型分类显示

- **命令配置**
  - 支持 PowerShell 命令格式
  - 可配置下载进度显示
  - 支持自动解压选项
  - 可设置链接过期时间（1小时到7天）
  - 支持自动复制文本文件内容到剪贴板
  - 支持为多文件自动创建文件夹

### 3. 系统设置
- **MinIO 配置**
  - 服务器地址设置
  - Access Key 配置
  - Secret Key 配置
  - 存储桶设置
  - HTTPS 安全连接选项

- **命令生成设置**
  - 显示下载进度选项
  - PowerShell 命令优先选项
  - 下载后自动删除选项

## 技术特点

### 1. 跨平台支持
- Windows 支持
  - 提供 .exe 可执行文件
  - Inno Setup 安装包
- macOS 支持
  - 提供 .app 应用包
  - DMG 安装包

### 2. 现代化界面
- 清晰的布局结构
- 响应式界面设计
- 美观的按钮和控件样式
- 支持拖放操作

### 3. 安全特性
- HTTPS 安全连接支持
- 临时访问链接生成
- 可配置的链接过期时间

### 4. 自动化构建
- GitHub Actions 自动构建
- 自动版本号生成
- 自动发布到 GitHub Releases

## 使用说明

### 安装
1. 从 GitHub Releases 下载最新版本
   - Windows 用户下载 .exe 安装包
   - macOS 用户下载 .dmg 安装包
2. 运行安装程序
3. 按照向导完成安装

### 初始配置
1. 首次运行时，进入设置页面
2. 配置 MinIO 服务器信息：
   - 服务器地址
   - Access Key
   - Secret Key
   - 存储桶名称
3. 点击"测试连接"确认配置正确

### 文件管理
1. 在主界面可以浏览所有文件
2. 使用搜索框和过滤器快速找到需要的文件
3. 右键点击文件可以进行各种操作

### 命令生成
1. 点击"添加文件"选择要分享的文件
2. 设置链接有效期
3. 选择需要的自动处理选项
4. 点击"生成命令"生成 PowerShell 命令
5. 复制命令到 PowerShell 中执行

## 开发信息

### 环境要求
- Python 3.10 或更高版本
- PyQt5
- MinIO Python SDK
- 其他依赖见 requirements.txt

### 构建说明
1. 克隆代码仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行开发版本：`python main.py`
4. 构建安装包：
   - Windows: `pyinstaller --name MyApp --onefile --noconsole --icon=resources\app.ico main.py`
   - macOS: `pyinstaller --name MyApp --windowed --icon=resources/app.ico main.py`

## 版本历史

### v1.0.0
- 初始版本发布
- 基本文件管理功能
- 命令生成功能
- Windows 和 macOS 支持

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。在提交之前，请：

1. 检查现有的 Issue 和 Pull Request
2. 遵循项目的代码风格
3. 编写清晰的提交信息
4. 添加必要的测试和文档

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
