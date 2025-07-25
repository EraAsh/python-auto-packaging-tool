# 自动化打包工具 / Auto Packaging Tool

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Release](https://img.shields.io/badge/release-v1.8.3-orange)](https://github.com/yourusername/auto-packager/releases)

## 项目概述 / Project Overview

**自动化打包工具**是一款功能强大的Python应用打包解决方案，旨在简化Python脚本到可执行文件的转换过程。支持PyInstaller和Nuitka两种打包引擎，提供智能依赖分析和现代化图形界面。

**Auto Packaging Tool** is a powerful Python application packaging solution designed to simplify the conversion of Python scripts to executable files. It supports both PyInstaller and Nuitka packaging engines, with intelligent dependency analysis and a modern graphical interface.

---

## 主要功能 / Key Features

### 🚀 一键打包体验 / One-Click Packaging
- 支持PyInstaller和Nuitka两种打包引擎  
  Supports both PyInstaller and Nuitka packaging engines
- 单文件或目录模式自由选择  
  Choice between single-file or directory mode
- 控制台/无窗口应用灵活切换  
  Flexible switching between console and windowed applications

### 🔍 智能依赖分析 / Intelligent Dependency Analysis
- 自动识别项目依赖关系  
  Automatically identifies project dependencies
- 智能推荐隐藏导入模块  
  Intelligently recommends hidden import modules
- 检测并提示缺失依赖项  
  Detects and prompts for missing dependencies

### ⚙️ 高级配置管理 / Advanced Configuration
- 保存/加载打包配置文件  
  Save/Load packaging configuration files
- 自定义输出程序名称  
  Customize output program name
- 添加应用程序图标  
  Add application icons
- 包含数据文件和文件夹  
  Include data files and folders

---

## 安装指南 / Installation Guide

### 前提条件 / Prerequisites
- Python 3.6+
- pip 20.0+

### 安装步骤 / Installation Steps
```bash
# 克隆仓库 / Clone repository
git clone https://github.com/yourusername/auto-packager.git

# 进入项目目录 / Enter project directory
cd auto-packager

# 安装依赖 / Install dependencies
pip install -r requirements.txt
