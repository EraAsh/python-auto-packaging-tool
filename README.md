# 自动化打包工具 / Auto Packaging Tool

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Release](https://img.shields.io/badge/release-v1.8.3-orange)](https://github.com/yourusername/auto-packager/releases)
[![Downloads](https://img.shields.io/badge/downloads-1k%2B-brightgreen)](https://github.com/yourusername/auto-packager/releases)

**自动化打包工具**是一款功能强大的Python应用打包解决方案，旨在简化Python脚本到可执行文件的转换过程。支持PyInstaller和Nuitka两种打包引擎，提供智能依赖分析和现代化图形界面。

**Auto Packaging Tool** is a powerful Python application packaging solution designed to simplify the conversion of Python scripts to executable files. It supports both PyInstaller and Nuitka packaging engines, with intelligent dependency analysis and a modern graphical interface.

![自动化打包工具界面](screenshot.png)

## 目录 / Table of Contents
- [功能亮点 / Key Features](#功能亮点--key-features)
- [安装指南 / Installation Guide](#安装指南--installation-guide)
- [使用说明 / Usage Instructions](#使用说明--usage-instructions)
- [系统要求 / System Requirements](#系统要求--system-requirements)
- [构建指南 / Building Guide](#构建指南--building-guide)
- [贡献指南 / Contributing](#贡献指南--contributing)
- [许可证 / License](#许可证--license)

## 功能亮点 / Key Features

### 🚀 一键打包体验 / One-Click Packaging
- **双引擎支持**：PyInstaller和Nuitka两种打包引擎  
  **Dual Engine Support**: Both PyInstaller and Nuitka packaging engines
- **灵活模式**：单文件或目录模式自由选择  
  **Flexible Modes**: Choice between single-file or directory mode
- **窗口选项**：控制台/无窗口应用灵活切换  
  **Window Options**: Flexible switching between console and windowed applications
- **输出定制**：自定义输出程序名称和图标  
  **Output Customization**: Customize output program name and icon

### 🔍 智能依赖分析 / Intelligent Dependency Analysis
- **自动识别**：自动识别项目依赖关系  
  **Auto Detection**: Automatically identifies project dependencies
- **智能推荐**：智能推荐隐藏导入模块  
  **Smart Recommendations**: Intelligently recommends hidden import modules
- **缺失检测**：检测并提示缺失依赖项  
  **Missing Detection**: Detects and prompts for missing dependencies
- **优化配置**：支持常见库(PyQt5, requests等)的优化配置  
  **Optimized Configuration**: Optimized configuration for common libraries (PyQt5, requests, etc.)

### ⚙️ 高级配置管理 / Advanced Configuration
- **配置保存**：保存/加载打包配置文件  
  **Config Save/Load**: Save/Load packaging configuration files
- **数据管理**：包含数据文件和文件夹  
  **Data Management**: Include data files and folders
- **体积优化**：排除不必要的模块以减小体积  
  **Size Optimization**: Exclude unnecessary modules to reduce size
- **UPX压缩**：支持UPX压缩减小可执行文件体积  
  **UPX Compression**: Support UPX compression to reduce executable size

### 🖥️ 现代化界面 / Modern Interface
- **直观设计**：精心设计的用户界面  
  **Intuitive Design**: Carefully designed user interface
- **实时监控**：实时打包输出监控  
  **Real-time Monitoring**: Real-time packaging output monitoring
- **高DPI支持**：支持高分辨率屏幕  
  **HiDPI Support**: Support for high-resolution screens
- **中文友好**：中文友好的操作环境  
  **Chinese-Friendly**: Chinese-friendly operating environment

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
```

### 依赖安装 / Dependency Installation
```bash
# 安装主要依赖 / Install main dependencies
pip install pyqt5 setuptools pkg_resources

# 可选：安装打包工具 / Optional: Install packaging tools
pip install pyinstaller nuitka
```

### 直接运行 / Direct Run
```bash
# 启动应用 / Launch application
python dabaoqi.py
```

## 使用说明 / Usage Instructions

### 基本使用流程 / Basic Workflow
1. **选择主文件** - 指定要打包的Python文件  
   **Select Main File** - Specify the Python file to package
2. **设置输出目录** - 选择打包结果保存位置  
   **Set Output Directory** - Choose where to save the packaged results
3. **配置打包选项** - 选择打包工具和模式  
   **Configure Packaging Options** - Select packaging tool and mode
4. **开始打包** - 点击"开始打包"按钮  
   **Start Packaging** - Click the "Start Packaging" button

### 打包选项说明 / Packaging Options

| 选项 / Option | 说明 / Description | 推荐设置 / Recommended |
|---------------|-------------------|------------------------|
| **打包工具**<br>Packaging Tool | PyInstaller(推荐)或Nuitka<br>PyInstaller(Recommended) or Nuitka | PyInstaller |
| **打包模式**<br>Packaging Mode | 单文件(便于分发)或目录模式(便于调试)<br>Single-file(for distribution) or Directory mode(for debugging) | 单文件/Single-file |
| **窗口模式**<br>Window Mode | 显示控制台或纯窗口应用<br>Show console or pure window application | 根据应用类型选择<br>Depending on application type |
| **智能依赖分析**<br>Intelligent Analysis | 自动识别并配置依赖<br>Automatically identify and configure dependencies | 开启/Enabled |
| **UPX压缩**<br>UPX Compression | 减小可执行文件体积<br>Reduce executable file size | 开启(如有UPX)<br>Enabled(if UPX available) |
| **自动添加缺失模块**<br>Auto Add Missing | 自动添加检测到的缺失模块<br>Automatically add detected missing modules | 开启/Enabled |

### 命令行构建 / Command Line Building
```bash
# 构建可执行文件 / Build executable
python dabao.py
```

## 系统要求 / System Requirements

| 组件 / Component | 要求 / Requirement |
|-----------------|-------------------|
| **操作系统**<br>Operating System | Windows 7/10/11, macOS 10.15+, Linux (需图形界面)<br>Windows 7/10/11, macOS 10.15+, Linux (with GUI) |
| **Python版本**<br>Python Version | Python 3.6+ |
| **内存**<br>Memory | 最低 2GB, 推荐 4GB+<br>Minimum 2GB, Recommended 4GB+ |
| **磁盘空间**<br>Disk Space | 最低 200MB, 推荐 500MB+<br>Minimum 200MB, Recommended 500MB+ |

## 构建指南 / Building Guide

要构建可执行文件，请执行以下步骤：  
To build the executable, follow these steps:

```bash
# 安装构建依赖 / Install build dependencies
pip install pyinstaller

# 运行构建脚本 / Run build script
python dabao.py
```

构建完成后，可执行文件将生成在 `dist` 目录：  
After building, the executable will be generated in the `dist` directory:

- Windows: `dist/自动化打包工具.exe`
- macOS/Linux: `dist/auto-packager`

### 构建选项 / Build Options
您可以通过修改 `dabao.py` 文件自定义构建：  
You can customize the build by modifying the `dabao.py` file:

```python
# 自定义图标 / Custom icon
icon_path = os.path.join(base_dir, "custom_icon.ico")

# 添加额外隐藏导入 / Add extra hidden imports
cmd.extend(['--hidden-import', 'additional_module'])

# 添加数据文件 / Add data files
cmd.extend(['--add-data', 'path/to/data;destination'])
```

## 贡献指南 / Contributing

我们欢迎各种形式的贡献！请遵循以下步骤：  
We welcome contributions of all kinds! Please follow these steps:

1. Fork 项目仓库  
   Fork the project repository
2. 创建新分支 (`git checkout -b feature/your-feature`)  
   Create your feature branch (`git checkout -b feature/your-feature`)
3. 提交变更 (`git commit -m 'Add some feature'`)  
   Commit your changes (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)  
   Push to the branch (`git push origin feature/your-feature`)
5. 创建 Pull Request  
   Create a Pull Request

### 开发依赖 / Development Dependencies
```bash
pip install -r dev-requirements.txt
```

### 代码风格 / Code Style
请遵循 PEP 8 编码规范：  
Please follow PEP 8 coding style:

```bash
# 使用 autopep8 格式化代码 / Format code with autopep8
autopep8 --in-place --aggressive --aggressive *.py
```

## 许可证 / License

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件  
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

```
MIT License

Copyright (c) 2025 Era Ash

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**自动化打包工具 - 让Python应用分发更简单**  
**Auto Packaging Tool - Making Python Application Distribution Easier**  
*© 2025 时绁打包工具开发团队 | 版本 v1.8.3*  
*© 2025 Era Ash | Version v1.8.3*
