#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import ast
import importlib.util
import time
import shutil
from typing import Dict, List, Any, Set, Tuple

# 确保 setuptools 已安装（包含 pkg_resources）
def ensure_setuptools():
    try:
        import pkg_resources
    except ImportError:
        print("正在安装 setuptools（包含 pkg_resources）...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
            import pkg_resources
            print("setuptools 安装成功！")
        except Exception as e:
            print(f"安装 setuptools 失败: {e}")
            sys.exit(1)

ensure_setuptools()

# 现在可以安全导入 pkg_resources
import pkg_resources

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("请安装PyQt5: pip install PyQt5")
    sys.exit(1)

class DependencyAnalyzer:
    """智能依赖分析器"""
    
    def __init__(self):
        self.builtin_modules = set(sys.builtin_module_names)
        self.stdlib_modules = self._get_stdlib_modules()
    
    def _get_stdlib_modules(self) -> Set[str]:
        """获取标准库模块列表"""
        stdlib_paths = [os.path.dirname(os.__file__)]
        if hasattr(sys, 'stdlib'):
            stdlib_paths.append(sys.stdlib)
        
        modules = set()
        for path in stdlib_paths:
            if os.path.exists(path):
                for name in os.listdir(path):
                    if name.endswith('.py') or os.path.isdir(os.path.join(path, name)):
                        module_name = name.split('.')[0]
                        if module_name not in ('__pycache__', 'site-packages'):
                            modules.add(module_name)
        return modules
    
    def analyze_file(self, file_path: str) -> Dict[str, List[str]]:
        """分析单个Python文件的依赖"""
        dependencies = {
            'imports': [],
            'from_imports': [],
            'missing': [],
            'third_party': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        dependencies['imports'].append(module_name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:
                        module_name = node.module.split('.')[0]
                        dependencies['from_imports'].append(module_name)
            
            # 检查第三方依赖
            all_imports = set(dependencies['imports'] + dependencies['from_imports'])
            for module in all_imports:
                if module in self.builtin_modules or module in self.stdlib_modules:
                    continue
                
                if self._is_third_party(module):
                    dependencies['third_party'].append(module)
                elif not self._is_available(module):
                    dependencies['missing'].append(module)
                    
        except Exception as e:
            print(f"分析文件失败 {file_path}: {e}")
            
        return dependencies
    
    def _is_third_party(self, module_name: str) -> bool:
        """检查是否为第三方模块"""
        try:
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                # 检查模块路径是否在site-packages或dist-packages中
                if 'site-packages' in spec.origin or 'dist-packages' in spec.origin:
                    return True
        except (ImportError, ValueError, TypeError):
            pass
        return False
    
    def _is_available(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def analyze_project(self, main_file: str) -> Dict[str, Any]:
        """分析整个项目的依赖"""
        project_dir = os.path.dirname(main_file)
        all_dependencies = {
            'third_party': set(),
            'missing': set(),
            'hidden_imports': set(),
            'files_analyzed': []
        }
        
        # 分析主文件和相关Python文件
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    deps = self.analyze_file(file_path)
                    
                    all_dependencies['third_party'].update(deps['third_party'])
                    all_dependencies['missing'].update(deps['missing'])
                    all_dependencies['files_analyzed'].append(file_path)
        
        # 智能推荐隐藏导入
        hidden_imports = set()
        for module in all_dependencies['third_party']:
            if module == 'PyQt5':
                # 修复：不要添加子模块，只添加顶层模块
                hidden_imports.add('PyQt5')
            elif module == 'requests':
                hidden_imports.update(['urllib3', 'certifi', 'chardet', 'idna'])
            elif module == 'pandas':
                hidden_imports.update(['pytz', 'numpy', 'dateutil'])
            elif module == 'numpy':
                hidden_imports.add('numpy')  # 只添加顶层模块
            elif module == 'PIL' or module == 'Pillow':
                hidden_imports.add('PIL')  # 只添加顶层模块
            elif module == 'matplotlib':
                hidden_imports.add('matplotlib')  # 只添加顶层模块
            elif module == 'sqlalchemy':
                hidden_imports.add('sqlalchemy')  # 只添加顶层模块
            elif module == 'scipy':
                hidden_imports.add('scipy')  # 只添加顶层模块
            elif module == 'bs4':
                hidden_imports.add('bs4')  # 只添加顶层模块
            elif module == 'lxml':
                hidden_imports.add('lxml')  # 只添加顶层模块
        
        # 添加常见的动态导入模块
        common_dynamic_imports = [
            'pkg_resources', 'xml.etree', 'email.mime', 
            'pandas._libs', 'numpy.random', 
            'scipy.special'
        ]
        hidden_imports.update(common_dynamic_imports)
        
        all_dependencies['hidden_imports'] = hidden_imports
        
        return {
            'third_party': list(all_dependencies['third_party']),
            'missing': list(all_dependencies['missing']),
            'hidden_imports': list(all_dependencies['hidden_imports']),
            'files_analyzed': all_dependencies['files_analyzed']
        }

class PackageWorker(QThread):
    """打包工作线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    error_details = pyqtSignal(str)
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.process = None
        self.error_output = []
        self.is_running = False
    
    def run(self):
        """执行打包"""
        self.is_running = True
        try:
            if self.config['packager'] == 'pyinstaller':
                success, message = self._run_pyinstaller()
            else:
                success, message = self._run_nuitka()
            
            if not success and self.error_output:
                error_details = '\n'.join(self.error_output[-20:])
                self.error_details.emit(error_details)
            
            self.finished.emit(success, message)
        except Exception as e:
            self.error_details.emit(str(e))
            self.finished.emit(False, f"打包异常: {str(e)}")
        finally:
            self.is_running = False
    
    def _run_pyinstaller(self) -> Tuple[bool, str]:
        """运行PyInstaller打包"""
        try:
            cmd = ['pyinstaller']
            
            if self.config.get('onefile', False):
                cmd.append('--onefile')
            
            if self.config.get('windowed', False):
                cmd.append('--windowed')
            elif self.config.get('console', True):
                cmd.append('--console')
            
            # 添加输出名称
            if self.config.get('output_name'):
                cmd.extend(['--name', self.config['output_name']])
            
            if self.config.get('output_dir'):
                cmd.extend(['--distpath', self.config['output_dir']])
            
            if self.config.get('icon_path') and os.path.exists(self.config['icon_path']):
                cmd.extend(['--icon', self.config['icon_path']])
            
            for hidden in self.config.get('hidden_imports', []):
                if hidden.strip():
                    # 修复：避免添加PyQt5子模块
                    if not hidden.startswith('PyQt5.Qt'):
                        cmd.extend(['--hidden-import', hidden.strip()])
            
            for data in self.config.get('add_data', []):
                if data.strip():
                    cmd.extend(['--add-data', data.strip()])
            
            for exclude in self.config.get('excludes', []):
                if exclude.strip():
                    cmd.extend(['--exclude-module', exclude.strip()])
            
            if self.config.get('clean', False):
                cmd.append('--clean')
            
            if self.config.get('upx_compress', False):
                cmd.append('--upx-dir=')
            
            if self.config.get('noconfirm', True):
                cmd.append('--noconfirm')
            
            cmd.append(self.config['main_file'])
            
            self.progress.emit(f"执行命令: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                cwd=os.path.dirname(self.config['main_file'])
            )
            
            while self.is_running:
                output = self.process.stdout.readline()
                if not output and self.process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    self.progress.emit(line)
                    
                    if 'error' in line.lower() or 'fail' in line.lower():
                        self.error_output.append(line)
            
            return_code = self.process.poll()
            
            if return_code == 0:
                return True, "打包成功完成！"
            else:
                return False, f"打包失败，返回码: {return_code}"
                
        except Exception as e:
            return False, f"PyInstaller执行失败: {str(e)}"
    
    def _run_nuitka(self) -> Tuple[bool, str]:
        """运行Nuitka打包 - 已修复包定位问题"""
        try:
            cmd = ['python', '-m', 'nuitka']
            
            # 添加打包模式参数
            if self.config.get('onefile', False):
                cmd.append('--onefile')
            else:
                cmd.append('--standalone')
            
            if self.config.get('windowed', False):
                cmd.append('--disable-console')
            
            # 输出目录
            if self.config.get('output_dir'):
                cmd.append(f'--output-dir={self.config["output_dir"]}')
            
            # 输出名称
            if self.config.get('output_name'):
                cmd.append(f'--output-filename={self.config["output_name"]}')
            
            # 图标
            if self.config.get('icon_path') and os.path.exists(self.config['icon_path']):
                cmd.append(f'--windows-icon-from-ico={self.config["icon_path"]}')
            
            # 启用必要插件
            cmd.append('--enable-plugin=pyqt5')
            cmd.append('--follow-imports')
            
            # 添加隐藏导入
            for hidden in self.config.get('hidden_imports', []):
                if hidden.strip():
                    # 修复：避免添加PyQt5子模块
                    if not hidden.startswith('PyQt5.Qt'):
                        # 尝试定位包路径
                        try:
                            module_spec = importlib.util.find_spec(hidden.strip())
                            if module_spec and module_spec.origin:
                                # 提取包目录
                                package_dir = os.path.dirname(module_spec.origin)
                                if 'site-packages' in package_dir or 'dist-packages' in package_dir:
                                    # 添加整个包目录
                                    cmd.append(f'--include-package-data={hidden.strip()}')
                                else:
                                    # 添加单个模块
                                    cmd.append(f'--include-module={hidden.strip()}')
                            else:
                                # 直接添加模块
                                cmd.append(f'--include-module={hidden.strip()}')
                        except (ImportError, ValueError, TypeError):
                            # 无法定位时直接添加模块
                            cmd.append(f'--include-module={hidden.strip()}')
            
            # 添加常见的必需模块
            required_modules = ['chardet', 'certifi', 'idna', 'urllib3']
            for mod in required_modules:
                if mod not in self.config.get('hidden_imports', []):
                    cmd.append(f'--include-module={mod}')
            
            # 数据文件处理
            for data in self.config.get('add_data', []):
                if data.strip():
                    try:
                        src, dst = data.split(';', 1)
                        src = src.strip()
                        dst = dst.strip()
                        
                        if os.path.isfile(src):
                            cmd.append(f'--include-data-file={src}={dst}')
                        elif os.path.isdir(src):
                            cmd.append(f'--include-data-dir={src}={dst}')
                        else:
                            self.progress.emit(f"⚠️ 数据源路径不存在: {src}")
                    except ValueError:
                        self.progress.emit(f"⚠️ 无效的数据文件格式: {data}")
            
            if self.config.get('clean', False):
                cmd.append('--remove-output')
            
            if self.config.get('upx_compress', False):
                cmd.append('--lto=yes')
            
            cmd.append(self.config['main_file'])
            
            self.progress.emit(f"执行命令: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                cwd=os.path.dirname(self.config['main_file'])
            )
            
            while self.is_running:
                output = self.process.stdout.readline()
                if not output and self.process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    self.progress.emit(line)
                    if 'error' in line.lower() or 'fail' in line.lower():
                        self.error_output.append(line)
            
            return_code = self.process.poll()
            
            if return_code == 0:
                return True, "打包成功完成！"
            else:
                return False, f"打包失败，返回码: {return_code}"
                
        except Exception as e:
            return False, f"Nuitka执行失败: {str(e)}"
    
    def stop(self):
        """停止打包进程"""
        self.is_running = False
        if self.process and self.process.poll() is None:
            try:
                # 先尝试正常终止
                self.process.terminate()
                
                # 等待5秒
                timeout = 5  # 5秒
                for _ in range(timeout * 10):
                    if self.process.poll() is not None:
                        return
                    time.sleep(0.1)
                
                # 如果还在运行，强制终止
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                print(f"停止进程时出错: {e}")

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "main_file": "",
            "output_dir": "",
            "output_name": "",  # 新增：输出程序名称
            "packager": "pyinstaller",
            "onefile": False,
            "console": True,
            "windowed": False,
            "icon_path": "",
            "hidden_imports": [],
            "add_data": [],
            "excludes": [],
            "clean": True,
            "noconfirm": True,
            "auto_analyze": True,
            "smart_exclude": True,
            "upx_compress": False,
            "auto_add_missing": True
        }
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 确保所有键都存在
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"配置加载失败: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 确保只保存有效的配置项
            valid_config = {}
            for key in self.default_config.keys():
                if key in config:
                    valid_config[key] = config[key]
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(valid_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False

class ChineseTextEdit(QTextEdit):
    """自定义中文文本编辑控件，提供中文上下文菜单"""
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        
        # 翻译菜单项为中文
        actions = menu.actions()
        translations = {
            "Undo": "撤销",
            "Redo": "重做",
            "Cut": "剪切",
            "Copy": "复制",
            "Paste": "粘贴",
            "Delete": "删除",
            "Select All": "全选"
        }
        
        for action in actions:
            text = action.text()
            if text in translations:
                action.setText(translations[text])
        
        menu.exec_(event.globalPos())

class ModernPackagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.worker = None
        
        self.init_ui()
        self.load_config()
        self.apply_modern_style()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🤖 py自动打包工具 v1.8.3")  # 更新版本号
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.create_header(main_layout)
        
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter, 1)  # 添加拉伸因子
        
        config_widget = self.create_config_panel()
        content_splitter.addWidget(config_widget)
        
        output_widget = self.create_output_panel()
        content_splitter.addWidget(output_widget)
        
        content_splitter.setSizes([500, 500])
        
        self.create_button_bar(main_layout)
        self.create_status_bar()
    
    def create_header(self, layout: QVBoxLayout):
        """创建标题区域"""
        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_layout = QHBoxLayout(header_widget)
        
        title_label = QLabel("🤖 py自动打包工具")
        title_label.setObjectName("title")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        version_label = QLabel("v1.8.3")  # 更新版本号
        version_label.setObjectName("version")
        version_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_widget)
    
    def create_config_panel(self) -> QScrollArea:
        """创建配置面板"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        config_layout.setSpacing(15)
        config_layout.setContentsMargins(10, 10, 10, 10)
        
        basic_group = self.create_basic_group()
        config_layout.addWidget(basic_group)
        
        advanced_group = self.create_advanced_group()
        config_layout.addWidget(advanced_group)
        
        optimization_group = self.create_optimization_group()
        config_layout.addWidget(optimization_group)
        
        config_layout.addStretch()
        scroll_area.setWidget(config_widget)
        
        return scroll_area
    
    def create_basic_group(self) -> QGroupBox:
        """创建基本设置组"""
        group = QGroupBox("📁 基本设置")
        group.setObjectName("modernGroup")
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 15, 10, 15)
        
        # 主文件选择
        main_file_layout = QHBoxLayout()
        self.main_file_edit = QLineEdit()
        self.main_file_edit.setPlaceholderText("选择要打包的Python主文件...")
        main_file_layout.addWidget(self.main_file_edit, 1)
        
        browse_btn = QPushButton("📂 浏览")
        browse_btn.setObjectName("modernButton")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self.browse_main_file)
        main_file_layout.addWidget(browse_btn)
        
        layout.addRow("主文件:", main_file_layout)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("选择输出目录...")
        output_layout.addWidget(self.output_dir_edit, 1)
        
        output_browse_btn = QPushButton("📂 浏览")
        output_browse_btn.setObjectName("modernButton")
        output_browse_btn.setFixedWidth(80)
        output_browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_browse_btn)
        
        layout.addRow("输出目录:", output_layout)
        
        # 输出程序名称（新增）
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("打包后的程序名称（可选）")
        layout.addRow("输出程序名称:", self.output_name_edit)
        
        # 打包工具选择
        packager_layout = QHBoxLayout()
        self.packager_group = QButtonGroup(self)  # 创建按钮组
        self.pyinstaller_radio = QRadioButton("PyInstaller")
        self.pyinstaller_radio.setChecked(True)
        self.packager_group.addButton(self.pyinstaller_radio)
        
        self.nuitka_radio = QRadioButton("Nuitka")
        self.packager_group.addButton(self.nuitka_radio)
        
        packager_layout.addWidget(self.pyinstaller_radio)
        packager_layout.addWidget(self.nuitka_radio)
        packager_layout.addStretch()
        
        layout.addRow("打包工具:", packager_layout)
        
        # 打包模式
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)  # 创建按钮组
        self.onefile_radio = QRadioButton("单文件模式")
        self.mode_group.addButton(self.onefile_radio)
        
        self.onedir_radio = QRadioButton("目录模式")
        self.onedir_radio.setChecked(True)
        self.mode_group.addButton(self.onedir_radio)
        
        mode_layout.addWidget(self.onefile_radio)
        mode_layout.addWidget(self.onedir_radio)
        mode_layout.addStretch()
        
        layout.addRow("打包模式:", mode_layout)
        
        # 窗口模式
        window_layout = QHBoxLayout()
        self.window_group = QButtonGroup(self)  # 创建按钮组
        self.console_radio = QRadioButton("显示控制台")
        self.console_radio.setChecked(True)
        self.window_group.addButton(self.console_radio)
        
        self.windowed_radio = QRadioButton("窗口模式")
        self.window_group.addButton(self.windowed_radio)
        
        window_layout.addWidget(self.console_radio)
        window_layout.addWidget(self.windowed_radio)
        window_layout.addStretch()
        
        layout.addRow("窗口设置:", window_layout)
        
        return group

    def on_packager_toggled(self):
        """打包工具切换"""
        # 两个打包工具都支持所有模式
        self.onefile_radio.setEnabled(True)
        self.onedir_radio.setEnabled(True)
        self.upx_compress_check.setEnabled(True)
        self.windowed_radio.setEnabled(True)
        self.console_radio.setEnabled(True)

    def on_mode_toggled(self):
        """打包模式切换"""
        # 这里可以添加模式切换时的额外逻辑
        pass
    
    def create_advanced_group(self) -> QGroupBox:
        """创建高级设置组"""
        group = QGroupBox("⚙️ 高级设置")
        group.setObjectName("modernGroup")
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 15, 10, 15)
        
        # 图标文件
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("选择应用图标文件 (.ico)...")
        icon_layout.addWidget(self.icon_edit, 1)
        
        icon_browse_btn = QPushButton("📂 浏览")
        icon_browse_btn.setObjectName("modernButton")
        icon_browse_btn.setFixedWidth(80)
        icon_browse_btn.clicked.connect(self.browse_icon_file)
        icon_layout.addWidget(icon_browse_btn)
        
        layout.addRow("应用图标:", icon_layout)
        
        # 隐藏导入 - 使用自定义中文文本编辑控件
        self.hidden_imports_edit = ChineseTextEdit()
        self.hidden_imports_edit.setMaximumHeight(80)
        self.hidden_imports_edit.setPlaceholderText("每行一个模块名，例如:\nrequests\nPyQt5.QtWebEngineWidgets")
        layout.addRow("隐藏导入:", self.hidden_imports_edit)
        
        # 添加数据文件
        data_files_layout = QVBoxLayout()
        
        self.data_files_list = QListWidget()
        self.data_files_list.setMaximumHeight(100)
        self.data_files_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        data_files_layout.addWidget(self.data_files_list)
        
        data_btn_layout = QHBoxLayout()
        
        add_file_btn = QPushButton("📄 添加文件")
        add_file_btn.setObjectName("modernButton")
        add_file_btn.clicked.connect(self.add_data_file)
        data_btn_layout.addWidget(add_file_btn)
        
        add_folder_btn = QPushButton("📁 添加文件夹")
        add_folder_btn.setObjectName("modernButton")
        add_folder_btn.clicked.connect(self.add_data_folder)
        data_btn_layout.addWidget(add_folder_btn)
        
        remove_data_btn = QPushButton("❌ 删除")
        remove_data_btn.setObjectName("modernButton")
        remove_data_btn.clicked.connect(self.remove_data_item)
        data_btn_layout.addWidget(remove_data_btn)
        
        data_files_layout.addLayout(data_btn_layout)
        layout.addRow("数据文件:", data_files_layout)
        
        # 排除模块 - 使用自定义中文文本编辑控件
        self.excludes_edit = ChineseTextEdit()
        self.excludes_edit.setMaximumHeight(60)
        self.excludes_edit.setPlaceholderText("每行一个要排除的模块名")
        layout.addRow("排除模块:", self.excludes_edit)
        
        return group

    def add_data_file(self):
        """添加数据文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择要打包的文件", "", "所有文件 (*)"
        )
        for file_path in files:
            if file_path:
                filename = os.path.basename(file_path)
                item_text = f"{file_path};{filename}"
                self.data_files_list.addItem(item_text)

    def add_data_folder(self):
        """添加数据文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择要打包的文件夹")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            item_text = f"{folder_path};{folder_name}"
            self.data_files_list.addItem(item_text)

    def remove_data_item(self):
        """删除选中的数据文件项"""
        selected_items = self.data_files_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            self.data_files_list.takeItem(self.data_files_list.row(item))
    
    def create_optimization_group(self) -> QGroupBox:
        """创建优化设置组"""
        group = QGroupBox("🚀 智能优化设置")
        group.setObjectName("modernGroup")
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 15, 10, 15)
        
        # 智能分析选项
        analysis_layout = QHBoxLayout()
        self.auto_analyze_check = QCheckBox("智能依赖分析")
        self.auto_analyze_check.setChecked(True)
        self.auto_analyze_check.setToolTip("默认开启！自动分析项目依赖并配置隐藏导入")
        
        self.analyze_btn = QPushButton("🔍 立即分析")
        self.analyze_btn.setObjectName("modernButton")
        self.analyze_btn.setToolTip("立即分析当前项目的依赖关系")
        self.analyze_btn.clicked.connect(self.analyze_dependencies)
        
        analysis_layout.addWidget(self.auto_analyze_check)
        analysis_layout.addWidget(self.analyze_btn)
        analysis_layout.addStretch()
        
        layout.addRow("依赖分析:", analysis_layout)
        
        # 清理选项
        options_layout = QHBoxLayout()
        self.clean_check = QCheckBox("清理临时文件")
        self.clean_check.setChecked(True)
        self.clean_check.setToolTip("默认开启！打包完成后自动清理临时文件")
        
        self.noconfirm_check = QCheckBox("不确认覆盖")
        self.noconfirm_check.setChecked(True)
        self.noconfirm_check.setToolTip("默认开启！如果输出文件已存在，直接覆盖而不询问")
        
        options_layout.addWidget(self.clean_check)
        options_layout.addWidget(self.noconfirm_check)
        options_layout.addStretch()
        
        layout.addRow("构建选项:", options_layout)
        
        # 智能优化选项
        smart_layout = QHBoxLayout()
        self.smart_exclude_check = QCheckBox("智能排除")
        self.smart_exclude_check.setChecked(True)
        self.smart_exclude_check.setToolTip("默认开启！自动排除不必要的模块以减小文件大小")
        
        self.upx_compress_check = QCheckBox("UPX压缩")
        self.upx_compress_check.setToolTip("使用UPX压缩可执行文件以减小体积")
        
        # 新增：自动添加缺失模块选项
        self.auto_add_missing_check = QCheckBox("自动添加缺失模块")
        self.auto_add_missing_check.setChecked(True)
        self.auto_add_missing_check.setToolTip("默认开启！自动添加检测到的缺失模块到打包配置")
        
        smart_layout.addWidget(self.smart_exclude_check)
        smart_layout.addWidget(self.upx_compress_check)
        smart_layout.addWidget(self.auto_add_missing_check)
        smart_layout.addStretch()
        
        layout.addRow("智能优化:", smart_layout)
        
        return group
    
    def create_output_panel(self) -> QWidget:
        """创建输出面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        output_group = QGroupBox("📋 打包输出")
        output_group.setObjectName("modernGroup")
        output_layout = QVBoxLayout(output_group)
        
        # 使用自定义中文文本编辑控件
        self.output_text = ChineseTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setObjectName("outputText")
        output_layout.addWidget(self.output_text)
        
        layout.addWidget(output_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        return widget
    
    def create_button_bar(self, layout: QVBoxLayout):
        """创建按钮栏"""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 5, 5, 5)
        
        save_config_btn = QPushButton("💾 保存配置")
        save_config_btn.setObjectName("modernButton")
        save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_config_btn)
        
        load_config_btn = QPushButton("📂 加载配置")
        load_config_btn.setObjectName("modernButton")
        load_config_btn.clicked.connect(self.load_config_from_file)
        button_layout.addWidget(load_config_btn)
        
        clear_btn = QPushButton("🧹 清空输出")
        clear_btn.setObjectName("modernButton")
        clear_btn.clicked.connect(self.clear_output)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_packaging)
        button_layout.addWidget(self.stop_btn)
        
        self.start_btn = QPushButton("🚀 开始打包")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self.start_packaging)
        button_layout.addWidget(self.start_btn)
        
        layout.addWidget(button_widget)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
    
    def browse_main_file(self):
        """浏览主文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python主文件", "", "Python文件 (*.py)"
        )
        if file_path:
            self.main_file_edit.setText(file_path)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def browse_icon_file(self):
        """浏览图标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "", "图标文件 (*.ico)"
        )
        if file_path:
            self.icon_edit.setText(file_path)
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        add_data = []
        for i in range(self.data_files_list.count()):
            item_text = self.data_files_list.item(i).text()
            add_data.append(item_text)
        
        config = {
            'main_file': self.main_file_edit.text().strip(),
            'output_dir': self.output_dir_edit.text().strip(),
            'output_name': self.output_name_edit.text().strip(),  # 新增
            'packager': 'pyinstaller' if self.pyinstaller_radio.isChecked() else 'nuitka',
            'onefile': self.onefile_radio.isChecked(),
            'console': self.console_radio.isChecked(),
            'windowed': self.windowed_radio.isChecked(),
            'icon_path': self.icon_edit.text().strip(),
            'clean': self.clean_check.isChecked(),
            'noconfirm': self.noconfirm_check.isChecked(),
            'auto_analyze': self.auto_analyze_check.isChecked(),
            'smart_exclude': self.smart_exclude_check.isChecked(),
            'upx_compress': self.upx_compress_check.isChecked(),
            'auto_add_missing': self.auto_add_missing_check.isChecked(),
            'hidden_imports': [line.strip() for line in self.hidden_imports_edit.toPlainText().split('\n') if line.strip()],
            'add_data': add_data,
            'excludes': [line.strip() for line in self.excludes_edit.toPlainText().split('\n') if line.strip()]
        }
        return config
    
    def set_config(self, config: Dict[str, Any]):
        """设置配置"""
        self.main_file_edit.setText(config.get('main_file', ''))
        self.output_dir_edit.setText(config.get('output_dir', ''))
        self.output_name_edit.setText(config.get('output_name', ''))  # 新增
        
        # 设置打包工具
        if config.get('packager') == 'nuitka':
            self.nuitka_radio.setChecked(True)
        else:
            self.pyinstaller_radio.setChecked(True)
        
        # 设置打包模式
        if config.get('onefile', False):
            self.onefile_radio.setChecked(True)
        else:
            self.onedir_radio.setChecked(True)
        
        # 设置窗口模式
        if config.get('windowed', False):
            self.windowed_radio.setChecked(True)
        else:
            self.console_radio.setChecked(True)
        
        self.icon_edit.setText(config.get('icon_path', ''))
        self.clean_check.setChecked(config.get('clean', True))
        self.noconfirm_check.setChecked(config.get('noconfirm', True))
        self.auto_analyze_check.setChecked(config.get('auto_analyze', True))
        self.smart_exclude_check.setChecked(config.get('smart_exclude', True))
        self.upx_compress_check.setChecked(config.get('upx_compress', False))
        self.auto_add_missing_check.setChecked(config.get('auto_add_missing', True))
        
        self.hidden_imports_edit.setPlainText('\n'.join(config.get('hidden_imports', [])))
        self.excludes_edit.setPlainText('\n'.join(config.get('excludes', [])))
        
        # 设置数据文件列表
        self.data_files_list.clear()
        for data_item in config.get('add_data', []):
            self.data_files_list.addItem(data_item)
    
    def save_config(self):
        """保存配置"""
        config = self.get_config()
        if self.config_manager.save_config(config):
            self.append_output("✅ 配置已保存")
        else:
            self.append_output("❌ 配置保存失败")
    
    def load_config(self):
        """加载配置"""
        config = self.config_manager.load_config()
        self.set_config(config)
    
    def load_config_from_file(self):
        """从文件加载配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置文件", "", "JSON文件 (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.set_config(config)
                self.append_output(f"✅ 配置已从 {file_path} 加载")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载配置失败: {str(e)}")
                self.append_output(f"❌ 配置加载失败: {str(e)}")
    
    def clear_output(self):
        """清空输出"""
        self.output_text.clear()
    
    def append_output(self, text: str):
        """添加输出文本"""
        self.output_text.append(text)
        self.output_text.ensureCursorVisible()
    
    def analyze_dependencies(self):
        """智能分析项目依赖"""
        main_file = self.main_file_edit.text().strip()
        if not main_file or not os.path.exists(main_file):
            QMessageBox.warning(self, "错误", "请先选择有效的主文件")
            return
        
        self.append_output("🔍 开始智能依赖分析...")
        
        try:
            analyzer = DependencyAnalyzer()
            result = analyzer.analyze_project(main_file)
            
            # 自动添加隐藏导入（仅添加智能推荐的模块）
            if result['hidden_imports']:
                current_hidden = self.hidden_imports_edit.toPlainText().strip()
                existing_imports = set()
                if current_hidden:
                    existing_imports = set(line.strip() for line in current_hidden.split('\n') if line.strip())
                
                # 只添加智能推荐的新模块（不包括缺失模块）
                new_imports = set(result['hidden_imports']) - existing_imports
                if new_imports:
                    all_imports = list(existing_imports) + list(new_imports)
                    self.hidden_imports_edit.setPlainText('\n'.join(sorted(all_imports)))
                    self.append_output(f"✅ 自动添加隐藏导入: {', '.join(sorted(new_imports))}")
            
            # 自动添加缺失模块（如果启用）
            if self.auto_add_missing_check.isChecked() and result['missing']:
                current_missing = self.hidden_imports_edit.toPlainText().strip()
                existing_missing = set()
                if current_missing:
                    existing_missing = set(line.strip() for line in current_missing.split('\n') if line.strip())
                
                # 只添加新的缺失模块
                missing_to_add = set(result['missing']) - existing_missing
                if missing_to_add:
                    new_text = current_missing + '\n' + '\n'.join(missing_to_add) if current_missing else '\n'.join(missing_to_add)
                    self.hidden_imports_edit.setPlainText(new_text)
                    self.append_output(f"⚠️ 自动添加缺失模块: {', '.join(missing_to_add)}")
            
            # 显示分析结果
            self.append_output(f"📊 分析完成:")
            self.append_output(f"   - 第三方依赖: {len(result['third_party'])} 个")
            if result['third_party']:
                self.append_output(f"     {', '.join(result['third_party'][:10])}{'...' if len(result['third_party']) > 10 else ''}")
            
            self.append_output(f"   - 缺失模块: {len(result['missing'])} 个")
            if result['missing']:
                self.append_output(f"     ⚠️ {', '.join(result['missing'])}")
            
            self.append_output(f"   - 推荐隐藏导入: {len(result['hidden_imports'])} 个")
            
            # 如果还有缺失模块，建议安装
            if result['missing']:
                self.append_output("💡 建议使用以下命令安装缺失模块:")
                for module in result['missing']:
                    self.append_output(f"    pip install {module}")
            
        except Exception as e:
            self.append_output(f"❌ 分析失败: {str(e)}")
    
    def start_packaging(self):
        """开始打包"""
        if self.worker and self.worker.isRunning():
            self.append_output("⚠️ 打包正在进行中，请等待完成或停止当前任务")
            return
            
        config = self.get_config()
        
        if not config['main_file']:
            QMessageBox.warning(self, "错误", "请选择要打包的Python主文件")
            return
        
        if not os.path.exists(config['main_file']):
            QMessageBox.warning(self, "错误", "主文件不存在")
            return
        
        # 智能分析
        if config['auto_analyze']:
            self.append_output("🤖 执行智能依赖分析...")
            self.analyze_dependencies()
            config = self.get_config()  # 重新获取配置，包含分析结果
        
        if not config['output_dir']:
            config['output_dir'] = os.path.join(os.path.dirname(config['main_file']), 'dist')
        
        # 创建输出目录
        try:
            os.makedirs(config['output_dir'], exist_ok=True)
        except Exception as e:
            self.append_output(f"❌ 创建输出目录失败: {str(e)}")
            return
        
        self.output_text.clear()
        self.append_output("🚀 开始打包...")
        self.append_output(f"📁 主文件: {config['main_file']}")
        self.append_output(f"📂 输出目录: {config['output_dir']}")
        self.append_output(f"🔧 打包工具: {config['packager'].upper()}")
        self.append_output(f"📦 打包模式: {'单文件' if config['onefile'] else '目录'}")
        self.append_output(f"🪟 窗口模式: {'窗口' if config['windowed'] else '控制台'}")
        
        # 显示自定义输出名称
        if config['output_name']:
            self.append_output(f"🏷️ 输出程序名称: {config['output_name']}")
        
        # 显示所有隐藏导入
        if config['hidden_imports']:
            self.append_output(f"🔍 隐藏导入: {', '.join(config['hidden_imports'])}")
        
        # 显示数据文件
        if config['add_data']:
            self.append_output(f"📎 数据文件: {len(config['add_data'])} 个")
            for data in config['add_data']:
                self.append_output(f"    - {data}")
        
        # 对于Nuitka打包的特殊提示
        if config['packager'] == 'nuitka':
            self.append_output("💡 提示: 正在使用Nuitka打包，自动添加常见必需模块")
        
        self.worker = PackageWorker(config)
        self.worker.progress.connect(self.append_output)
        self.worker.finished.connect(self.on_packaging_finished)
        self.worker.error_details.connect(self.show_error_details)
        self.worker.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.status_bar.showMessage("正在打包...")
    
    def stop_packaging(self):
        """停止打包"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.append_output("⏹️ 正在停止打包进程...")
        else:
            self.append_output("⚠️ 没有正在运行的打包进程")
    
    def on_packaging_finished(self, success: bool, message: str):
        """打包完成回调"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.append_output(f"✅ {message}")
            self.status_bar.showMessage("打包成功")
            
            reply = QMessageBox.question(
                self, "打包完成", 
                f"{message}\n\n是否打开输出目录？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                output_dir = self.output_dir_edit.text().strip()
                if not output_dir:
                    output_dir = os.path.join(os.path.dirname(self.main_file_edit.text()), 'dist')
                
                if os.path.exists(output_dir):
                    if sys.platform == "win32":
                        os.startfile(output_dir)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", output_dir])
                    else:
                        subprocess.run(["xdg-open", output_dir])
        else:
            self.append_output(f"❌ {message}")
            self.status_bar.showMessage("打包失败")
    
    def show_error_details(self, error_details: str):
        """显示错误详情"""
        self.append_output("=" * 60)
        self.append_output("📋 详细错误信息:")
        self.append_output(error_details)
        self.append_output("=" * 60)
    
    def apply_modern_style(self):
        """应用现代化样式"""
        style = """
        QMainWindow {
            background-color: #f5f7fa;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }
        
        #header {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #1abc9c);
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 15px;
        }
        
        #title {
            color: white;
            font-size: 22px;
            font-weight: bold;
            padding: 5px 0;
        }
        
        #version {
            color: rgba(255, 255, 255, 0.85);
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.15);
            padding: 3px 8px;
            border-radius: 10px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #d1d8e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 8px;
            background-color: transparent;
            color: #2c3e50;
            font-size: 14px;
        }
        
        #modernGroup {
            border: 1px solid #a0d2eb;
            background-color: #f9fdff;
        }
        
        #modernGroup::title {
            color: #2980b9;
        }
        
        QPushButton {
            background-color: #e0e7ff;
            color: #4a69bd;
            border: 1px solid #cad3ff;
            border-radius: 6px;
            padding: 7px 14px;
            font-weight: 500;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #d0d9ff;
            border-color: #a5b4fc;
        }
        
        QPushButton:pressed {
            background-color: #c0ccff;
        }
        
        #modernButton {
            background-color: #4a69bd;
            color: white;
            border: 1px solid #3c5aa6;
        }
        
        #modernButton:hover {
            background-color: #3c5aa6;
        }
        
        #modernButton:pressed {
            background-color: #2e4a8e;
        }
        
        #startButton {
            background-color: #27ae60;
            color: white;
            border: 1px solid #219653;
            font-weight: bold;
            padding: 8px 20px;
        }
        
        #startButton:hover {
            background-color: #219653;
        }
        
        #stopButton {
            background-color: #e74c3c;
            color: white;
            border: 1px solid #c0392b;
            font-weight: bold;
            padding: 8px 20px;
        }
        
        #stopButton:hover {
            background-color: #c0392b;
        }
        
        QLineEdit, QTextEdit, QListWidget {
            border: 1px solid #d1d8e0;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
            font-size: 13px;
        }
        
        QLineEdit:focus, QTextEdit:focus, QListWidget:focus {
            border-color: #4a69bd;
        }
        
        QTextEdit {
            font-family: 'Consolas', 'Courier New', monospace;
        }
        
        #outputText {
            background-color: #2c3e50;
            color: #ecf0f1;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            border: 1px solid #34495e;
        }
        
        QProgressBar {
            border: 1px solid #d1d8e0;
            border-radius: 4px;
            text-align: center;
            background-color: #f1f3f6;
        }
        
        QProgressBar::chunk {
            background-color: #4a69bd;
            border-radius: 3px;
        }
        
        QRadioButton, QCheckBox {
            spacing: 6px;
            font-weight: normal;
        }
        
        QRadioButton::indicator, QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QRadioButton::indicator {
            border-radius: 9px;
            border: 2px solid #7f8c8d;
        }
        
        QRadioButton::indicator:checked {
            background-color: #4a69bd;
            border: 2px solid #4a69bd;
        }
        
        QCheckBox::indicator {
            border-radius: 4px;
            border: 2px solid #7f8c8d;
        }
        
        QCheckBox::indicator:checked {
            background-color: #4a69bd;
            border: 2px solid #4a69bd;
        }
        
        QScrollArea {
            border: none;
        }
        
        QSplitter::handle {
            background-color: #d1d8e0;
        }
        """
        self.setStyleSheet(style)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("py自动打包工具")
    app.setApplicationVersion("1.8.3")
    
    # 设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = ModernPackagerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()