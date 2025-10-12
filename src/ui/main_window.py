#!/usr/bin/env python3
"""
LAM-Agent 高级图形用户界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
from typing import Optional, Dict, Any
import json
import webbrowser
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.agent.lam_agent import LamAgent
from ..tools.executor import executor
from ..tools.command_recognizer import CommandRecognizer, CommandType


class LAMAgentUI:
    def __init__(self, root):
        self.root = root
        self.agent: Optional[LamAgent] = None
        self.conversation_history = []
        self.command_recognizer = CommandRecognizer()
        self.setup_ui()
        self.setup_agent()
        
    def setup_ui(self):
        """设置高级用户界面"""
        self.root.title("LAM-Agent Pro - DeepSeek 智能助手")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 创建侧边栏
        self.create_sidebar(main_frame)
        
        # 创建主聊天区域
        self.create_chat_area(main_frame)
        
        # 创建底部输入区域
        self.create_input_area(main_frame)
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建对话", command=self.new_conversation)
        file_menu.add_command(label="保存对话", command=self.save_conversation)
        file_menu.add_command(label="加载对话", command=self.load_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="导出日志", command=self.export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空对话", command=self.clear_conversation)
        edit_menu.add_command(label="复制选中", command=self.copy_selected)
        edit_menu.add_command(label="全选", command=self.select_all)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="配置", command=self.open_config)
        tools_menu.add_command(label="测试连接", command=self.test_connection)
        tools_menu.add_command(label="查看日志", command=self.view_logs)
        tools_menu.add_separator()
        tools_menu.add_command(label="网页自动化...", command=self.open_automation_dialog)
        tools_menu.add_command(label="桌面管理...", command=self.open_desktop_dialog)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="快捷键", command=self.show_shortcuts)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_sidebar(self, parent):
        """创建侧边栏"""
        sidebar = ttk.LabelFrame(parent, text="功能面板", padding="10")
        sidebar.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 桌面操作按钮
        ttk.Label(sidebar, text="桌面操作", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        desktop_btn_frame = ttk.Frame(sidebar)
        desktop_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(desktop_btn_frame, text="扫描桌面", 
                  command=lambda: self._quick_scan_desktop()).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(desktop_btn_frame, text="搜索文件", 
                  command=lambda: self._quick_search_files()).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(desktop_btn_frame, text="启动文件", 
                  command=lambda: self._quick_launch_file()).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(desktop_btn_frame, text="桌面管理", 
                  command=self.open_desktop_dialog).pack(fill=tk.X, pady=(0, 2))
        
        # 分隔线
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 对话历史
        ttk.Label(sidebar, text="对话历史", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # 历史列表
        history_frame = ttk.Frame(sidebar)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_listbox = tk.Listbox(history_frame, height=8)
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                        command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 历史操作按钮
        history_btn_frame = ttk.Frame(sidebar)
        history_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(history_btn_frame, text="加载", 
                  command=self.load_history_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(history_btn_frame, text="删除", 
                  command=self.delete_history_item).pack(side=tk.LEFT)
    
    def create_chat_area(self, parent):
        """创建聊天区域"""
        chat_frame = ttk.LabelFrame(parent, text="对话区域", padding="10")
        chat_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # 聊天文本区域
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, 
            font=("Consolas", 11),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#ffffff'
        )
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置文本标签样式
        self.chat_text.tag_configure("user", foreground="#0066cc", font=("Arial", 11, "bold"))
        self.chat_text.tag_configure("ai", foreground="#009900", font=("Arial", 11))
        self.chat_text.tag_configure("system", foreground="#666666", font=("Arial", 10, "italic"))
        self.chat_text.tag_configure("error", foreground="#cc0000", font=("Arial", 11, "bold"))
        self.chat_text.tag_configure("info", foreground="#666666", font=("Arial", 10))
        self.chat_text.tag_configure("success", foreground="#006600", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("warning", foreground="#ff6600", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("timestamp", foreground="#999999", font=("Arial", 9))
        self.chat_text.tag_configure("separator", foreground="#cccccc")
        
        # 绑定右键菜单
        self.create_context_menu()
    
    def create_input_area(self, parent):
        """创建输入区域"""
        input_frame = ttk.LabelFrame(parent, text="输入区域", padding="10")
        input_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # 输入文本框
        self.input_text = tk.Text(input_frame, height=4, wrap=tk.WORD, 
                                 font=("Arial", 11))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 命令建议框架
        self.suggestion_frame = ttk.Frame(input_frame)
        self.suggestion_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 命令建议标签
        self.suggestion_label = ttk.Label(self.suggestion_frame, text="命令建议:", 
                                         font=("Arial", 9, "italic"), foreground="gray")
        self.suggestion_label.pack(anchor=tk.W)
        
        # 命令建议按钮框架
        self.suggestion_buttons_frame = ttk.Frame(self.suggestion_frame)
        self.suggestion_buttons_frame.pack(fill=tk.X, pady=(2, 0))
        
        # 输入滚动条
        input_scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, 
                                      command=self.input_text.yview)
        input_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.input_text.configure(yscrollcommand=input_scrollbar.set)
        
        # 按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=2, sticky=(tk.N, tk.S))
        
        self.send_button = ttk.Button(button_frame, text="发送\n(Ctrl+Enter)", 
                                    command=self.send_message, width=12)
        self.send_button.pack(pady=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="清空", 
                                     command=self.clear_input, width=12)
        self.clear_button.pack()
        
        # 绑定快捷键
        # ChatGPT风格：Enter 发送，Shift+Enter 换行
        def _on_return(e):
            if e.state & 0x0001:  # Shift
                return  # 允许换行
            self.send_message()
            return "break"
        self.input_text.bind('<Return>', _on_return)
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
        self.input_text.bind('<Control-a>', lambda e: self.select_all())
        self.input_text.bind('<Control-c>', lambda e: self.copy_selected())
        
        # 绑定文本变化事件，用于命令识别和建议
        self.input_text.bind('<KeyRelease>', self._on_input_change)
        self.input_text.bind('<FocusIn>', self._on_input_focus)
        
        # 设置焦点
        self.input_text.focus()
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 状态信息
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # 连接状态
        self.connection_var = tk.StringVar()
        self.connection_var.set("未连接")
        connection_label = ttk.Label(self.status_frame, textvariable=self.connection_var,
                                   foreground="red")
        connection_label.pack(side=tk.LEFT, padx=20)
        
        # 时间显示
        self.time_var = tk.StringVar()
        self.update_time()
        time_label = ttk.Label(self.status_frame, textvariable=self.time_var)
        time_label.pack(side=tk.RIGHT, padx=5)
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.chat_text, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selected)
        self.context_menu.add_command(label="全选", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="清空对话", command=self.clear_conversation)
        self.context_menu.add_command(label="保存对话", command=self.save_conversation)
        
        self.chat_text.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def setup_agent(self):
        """初始化LAM Agent"""
        try:
            # 使用环境变量与 .env 配置，不在代码中硬编码密钥
            self.agent = LamAgent()
            self.connection_var.set("已连接")
            self.connection_var.set("已连接")
            self.add_to_chat("系统", "LAM-Agent 已成功连接！", "system")
            
        except Exception as e:
            self.connection_var.set("连接失败")
            self.add_to_chat("系统", f"连接失败: {str(e)}", "error")
    
    def quick_action(self, action):
        """快速操作"""
        actions = {
            "search": "搜索最新的信息",
            "browse": "分析这个网页的内容",
            "open_website": "打开网站",
            "create_file": "创建文件",
            "calculate": "计算数学表达式",
            "translate": "翻译文本",
            "run_command": "运行系统命令",
            "get_weather": "获取天气信息",
            "bilibili_play": "B站搜索并播放(关键词)"
        }
        
        if action == "bilibili_play":
            try:
                keyword = tk.simpledialog.askstring("B站搜索并播放", "请输入关键词：", parent=self.root)
                if not keyword:
                    return
                self.add_to_chat("系统", f"开始在B站搜索并播放: {keyword}", "info")
                threading.Thread(target=self._run_bilibili_play_task, args=(keyword,), daemon=True).start()
            except Exception as e:
                self.add_to_chat("系统", f"操作失败: {e}", "error")
            return
        
        if action in actions:
            self.input_text.insert(tk.END, actions[action])
            self.input_text.focus()

    def _run_bilibili_play_task(self, keyword: str):
        try:
            res = executor.execute_action("bilibili_search_play", {"keyword": keyword})
            msg = res.get("message", "已执行")
            logs = res.get("logs")
            self.add_to_chat("系统", msg, "success")
            if logs:
                self.add_to_chat("系统", "执行日志:\n" + "\n".join(logs[-20:]), "info")
        except Exception as e:
            self.add_to_chat("系统", f"执行失败: {e}", "error")

    # ---------- 网页自动化对话框 ----------
    def open_automation_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("网页自动化 (nl_automate)")
        win.geometry("520x520")
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="初始URL").grid(row=0, column=0, sticky=tk.W)
        url_var = tk.StringVar()
        url_entry = ttk.Entry(frm, textvariable=url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frm, text="自然语言指令 (query)").grid(row=1, column=0, sticky=tk.W)
        query_txt = tk.Text(frm, height=3)
        query_txt.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # 登录信息
        login_frame = ttk.LabelFrame(frm, text="可选登录信息", padding=8)
        login_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=8)
        for c in range(2):
            login_frame.columnconfigure(c, weight=1)
        user_var = tk.StringVar(); pass_var = tk.StringVar()
        u_sel_var = tk.StringVar(); p_sel_var = tk.StringVar(); s_sel_var = tk.StringVar()
        ttk.Label(login_frame, text="用户名").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(login_frame, textvariable=user_var).grid(row=0, column=1, sticky=tk.EW)
        ttk.Label(login_frame, text="密码").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(login_frame, textvariable=pass_var, show="*").grid(row=1, column=1, sticky=tk.EW)
        ttk.Label(login_frame, text="用户名选择器").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(login_frame, textvariable=u_sel_var).grid(row=2, column=1, sticky=tk.EW)
        ttk.Label(login_frame, text="密码选择器").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(login_frame, textvariable=p_sel_var).grid(row=3, column=1, sticky=tk.EW)
        ttk.Label(login_frame, text="提交按钮选择器").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(login_frame, textvariable=s_sel_var).grid(row=4, column=1, sticky=tk.EW)

        # 自定义 steps
        ttk.Label(frm, text="自定义 Steps (JSON数组，可留空)").grid(row=3, column=0, sticky=tk.W)
        steps_txt = tk.Text(frm, height=6)
        steps_txt.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # 日志视图
        log_box = scrolledtext.ScrolledText(frm, height=10, state=tk.DISABLED)
        log_box.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, pady=(8,0))

        def append_log(text: str):
            log_box.configure(state=tk.NORMAL)
            log_box.insert(tk.END, text + "\n")
            log_box.configure(state=tk.DISABLED)
            log_box.see(tk.END)

        def run_automation():
            import json as _json
            query = query_txt.get("1.0", tk.END).strip()
            url = url_var.get().strip()
            steps = steps_txt.get("1.0", tk.END).strip()
            auth = None
            if user_var.get().strip() and pass_var.get().strip() and u_sel_var.get().strip() and p_sel_var.get().strip():
                auth = {
                    "username": user_var.get().strip(),
                    "password": pass_var.get().strip(),
                    "username_selector": u_sel_var.get().strip(),
                    "password_selector": p_sel_var.get().strip(),
                }
                if s_sel_var.get().strip():
                    auth["submit_selector"] = s_sel_var.get().strip()
            try:
                parsed_steps = _json.loads(steps) if steps else []
            except Exception:
                parsed_steps = []
                append_log("自定义 steps 解析失败，已忽略")

            params = {"query": query}
            if url:
                params["url"] = url
            if auth:
                params["auth"] = auth
            if parsed_steps:
                params["steps"] = parsed_steps

            append_log("开始执行 nl_automate …")
            def _task():
                try:
                    res = executor.execute_action("nl_automate", params)
                    for line in (res.get("logs") or [])[-50:]:
                        append_log(line)
                    append_log(f"结果: success={res.get('success', True)} title={res.get('title')} url={res.get('current_url')}")
                except Exception as e:
                    append_log(f"执行失败: {e}")
            threading.Thread(target=_task, daemon=True).start()

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, sticky=tk.EW)
        ttk.Button(btns, text="运行自动化", command=run_automation).pack(side=tk.LEFT)
        def run_bili():
            kw = query_txt.get("1.0", tk.END).strip() or "热门"
            threading.Thread(target=self._run_bilibili_play_task, args=(kw,), daemon=True).start()
        ttk.Button(btns, text="B站搜索并播放(用上方关键词)", command=run_bili).pack(side=tk.LEFT, padx=8)

    # ---------- 桌面管理对话框 ----------
    def open_desktop_dialog(self):
        """打开桌面管理对话框"""
        win = tk.Toplevel(self.root)
        win.title("桌面文件管理")
        win.geometry("800x600")
        win.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(win, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 扫描桌面标签页
        scan_frame = ttk.Frame(notebook, padding="10")
        notebook.add(scan_frame, text="扫描桌面")
        
        # 扫描按钮
        scan_btn_frame = ttk.Frame(scan_frame)
        scan_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(scan_btn_frame, text="扫描桌面文件", 
                  command=lambda: self._scan_desktop_files(scan_result_text)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(scan_btn_frame, text="获取摘要", 
                  command=lambda: self._get_desktop_summary(scan_result_text)).pack(side=tk.LEFT)
        
        # 扫描结果显示
        ttk.Label(scan_frame, text="扫描结果:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        scan_result_text = scrolledtext.ScrolledText(scan_frame, height=20, state=tk.DISABLED)
        scan_result_text.pack(fill=tk.BOTH, expand=True)
        
        # 搜索桌面标签页
        search_frame = ttk.Frame(notebook, padding="10")
        notebook.add(search_frame, text="搜索桌面")
        
        # 搜索输入
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_input_frame, text="搜索关键词:").pack(side=tk.LEFT, padx=(0, 10))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_input_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(search_input_frame, text="搜索", 
                  command=lambda: self._search_desktop_files(search_var.get(), search_result_text)).pack(side=tk.LEFT)
        
        # 搜索结果
        ttk.Label(search_frame, text="搜索结果:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        search_result_text = scrolledtext.ScrolledText(search_frame, height=20, state=tk.DISABLED)
        search_result_text.pack(fill=tk.BOTH, expand=True)
        
        # 启动文件标签页
        launch_frame = ttk.Frame(notebook, padding="10")
        notebook.add(launch_frame, text="启动文件")
        
        # 启动输入
        launch_input_frame = ttk.Frame(launch_frame)
        launch_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(launch_input_frame, text="文件名:").pack(side=tk.LEFT, padx=(0, 10))
        launch_var = tk.StringVar()
        launch_entry = ttk.Entry(launch_input_frame, textvariable=launch_var, width=30)
        launch_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(launch_input_frame, text="启动", 
                  command=lambda: self._launch_desktop_file(launch_var.get(), launch_result_text)).pack(side=tk.LEFT)
        
        # 启动结果显示
        ttk.Label(launch_frame, text="启动结果:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        launch_result_text = scrolledtext.ScrolledText(launch_frame, height=20, state=tk.DISABLED)
        launch_result_text.pack(fill=tk.BOTH, expand=True)
        
        # 快速操作标签页
        quick_frame = ttk.Frame(notebook, padding="10")
        notebook.add(quick_frame, text="快速操作")
        
        # 快速操作按钮
        quick_btn_frame = ttk.Frame(quick_frame)
        quick_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(quick_btn_frame, text="扫描桌面", 
                  command=lambda: self._quick_scan_desktop()).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(quick_btn_frame, text="搜索Python文件", 
                  command=lambda: self._quick_search_python()).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(quick_btn_frame, text="搜索可执行文件", 
                  command=lambda: self._quick_search_executable()).pack(side=tk.LEFT)
        
        # 快速操作结果显示
        ttk.Label(quick_frame, text="操作结果:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        quick_result_text = scrolledtext.ScrolledText(quick_frame, height=20, state=tk.DISABLED)
        quick_result_text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定回车键到搜索
        search_entry.bind('<Return>', lambda e: self._search_desktop_files(search_var.get(), search_result_text))
        launch_entry.bind('<Return>', lambda e: self._launch_desktop_file(launch_var.get(), launch_result_text))
        
        # 初始化时扫描桌面
        self._scan_desktop_files(scan_result_text)
    
    def _append_to_text(self, text_widget, message, tag="normal"):
        """添加文本到文本控件"""
        text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, message + "\n", tag)
        text_widget.configure(state=tk.DISABLED)
        text_widget.see(tk.END)
    
    def _scan_desktop_files(self, result_text):
        """扫描桌面文件"""
        def _task():
            try:
                from src.tools.desktop_integration import DesktopIntegration
                integration = DesktopIntegration()
                result = integration.scan_desktop()
                
                result_text.configure(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.configure(state=tk.DISABLED)
                
                if result['success']:
                    self._append_to_text(result_text, f"[SUCCESS] {result['message']}", "success")
                    if result.get('files'):
                        self._append_to_text(result_text, f"\n找到 {len(result['files'])} 个文件/快捷方式:")
                        for i, file_info in enumerate(result['files'], 1):
                            file_type = "[SHORTCUT]" if file_info.get('type') == 'shortcut' else "[FILE]"
                            executable = "[EXE]" if file_info.get('executable') else ""
                            self._append_to_text(result_text, f"{i:2d}. {file_type} {file_info['name']} {executable}")
                            if file_info.get('description'):
                                self._append_to_text(result_text, f"     {file_info['description']}")
                else:
                    self._append_to_text(result_text, f"[ERROR] {result['error']}", "error")
                    
            except Exception as e:
                self._append_to_text(result_text, f"[ERROR] 扫描失败: {str(e)}", "error")
        
        threading.Thread(target=_task, daemon=True).start()
    
    def _get_desktop_summary(self, result_text):
        """获取桌面文件摘要"""
        def _task():
            try:
                from src.tools.desktop_integration import DesktopIntegration
                integration = DesktopIntegration()
                result = integration.get_desktop_files_summary()
                
                if result['success']:
                    self._append_to_text(result_text, "\n" + "="*50, "separator")
                    self._append_to_text(result_text, "[INFO] 桌面文件摘要:", "info")
                    self._append_to_text(result_text, f"总文件数: {result['total_files']}")
                    self._append_to_text(result_text, f"可执行文件数: {result['executable_files']}")
                    self._append_to_text(result_text, f"桌面路径: {result['desktop_path']}")
                    self._append_to_text(result_text, "文件类型统计:")
                    for file_type, count in result['type_statistics'].items():
                        self._append_to_text(result_text, f"  {file_type}: {count} 个")
                else:
                    self._append_to_text(result_text, f"[ERROR] {result['error']}", "error")
                    
            except Exception as e:
                self._append_to_text(result_text, f"[ERROR] 获取摘要失败: {str(e)}", "error")
        
        threading.Thread(target=_task, daemon=True).start()
    
    def _search_desktop_files(self, keyword, result_text):
        """搜索桌面文件"""
        if not keyword.strip():
            self._append_to_text(result_text, "[WARNING] 请输入搜索关键词", "warning")
            return
            
        def _task():
            try:
                from src.tools.desktop_integration import DesktopIntegration
                integration = DesktopIntegration()
                result = integration.search_desktop(f"搜索桌面 {keyword}")
                
                result_text.configure(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.configure(state=tk.DISABLED)
                
                if result['success']:
                    self._append_to_text(result_text, f"[SUCCESS] {result['message']}", "success")
                    if result.get('files'):
                        self._append_to_text(result_text, f"\n匹配的文件:")
                        for i, file_info in enumerate(result['files'], 1):
                            file_type = "[SHORTCUT]" if file_info.get('type') == 'shortcut' else "[FILE]"
                            executable = "[EXE]" if file_info.get('executable') else ""
                            self._append_to_text(result_text, f"{i:2d}. {file_type} {file_info['name']} {executable}")
                            if file_info.get('description'):
                                self._append_to_text(result_text, f"     {file_info['description']}")
                else:
                    self._append_to_text(result_text, f"[ERROR] {result['error']}", "error")
                    
            except Exception as e:
                self._append_to_text(result_text, f"[ERROR] 搜索失败: {str(e)}", "error")
        
        threading.Thread(target=_task, daemon=True).start()
    
    def _launch_desktop_file(self, filename, result_text):
        """启动桌面文件"""
        if not filename.strip():
            self._append_to_text(result_text, "[WARNING] 请输入文件名", "warning")
            return
            
        def _task():
            try:
                from src.tools.desktop_integration import DesktopIntegration
                integration = DesktopIntegration()
                result = integration.launch_from_command(f"启动 {filename}")
                
                result_text.configure(state=tk.NORMAL)
                result_text.delete(1.0, tk.END)
                result_text.configure(state=tk.DISABLED)
                
                if result['success']:
                    self._append_to_text(result_text, f"[SUCCESS] {result['message']}", "success")
                    if result.get('launch_result'):
                        launch_result = result['launch_result']
                        if launch_result.get('process_id'):
                            self._append_to_text(result_text, f"进程ID: {launch_result['process_id']}")
                        if launch_result.get('command'):
                            self._append_to_text(result_text, f"执行命令: {launch_result['command']}")
                else:
                    self._append_to_text(result_text, f"[ERROR] {result['error']}", "error")
                    
            except Exception as e:
                self._append_to_text(result_text, f"[ERROR] 启动失败: {str(e)}", "error")
        
        threading.Thread(target=_task, daemon=True).start()
    
    def _quick_scan_desktop(self):
        """快速扫描桌面"""
        self.add_to_chat("系统", "正在扫描桌面文件...", "info")
        if self.agent:
            threading.Thread(target=self._run_desktop_command, args=("扫描桌面文件",), daemon=True).start()
    
    def _quick_search_python(self):
        """快速搜索Python文件"""
        self.add_to_chat("系统", "正在搜索Python文件...", "info")
        if self.agent:
            threading.Thread(target=self._run_desktop_command, args=("搜索桌面文件 python",), daemon=True).start()
    
    def _quick_search_executable(self):
        """快速搜索可执行文件"""
        self.add_to_chat("系统", "正在搜索可执行文件...", "info")
        if self.agent:
            threading.Thread(target=self._run_desktop_command, args=("搜索桌面文件 exe",), daemon=True).start()
    
    def _run_desktop_command(self, command):
        """运行桌面命令"""
        try:
            result = self.agent.run(command)
            self.add_to_chat("AI", result['answer'], "ai")
        except Exception as e:
            self.add_to_chat("系统", f"执行失败: {str(e)}", "error")
    
    def _on_input_change(self, event):
        """输入文本变化时的处理"""
        # 延迟处理，避免频繁触发
        self.root.after(300, self._update_command_suggestions)
    
    def _on_input_focus(self, event):
        """输入框获得焦点时的处理"""
        self._update_command_suggestions()
    
    def _update_command_suggestions(self):
        """更新命令建议"""
        try:
            current_text = self.input_text.get("1.0", tk.END).strip()
            
            # 清除现有建议按钮
            for widget in self.suggestion_buttons_frame.winfo_children():
                widget.destroy()
            
            if not current_text:
                self.suggestion_label.config(text="命令建议: 输入命令获取建议")
                return
            
            # 获取命令建议
            suggestions = self.command_recognizer.get_command_suggestions(current_text)
            
            if suggestions:
                self.suggestion_label.config(text=f"命令建议: 找到 {len(suggestions)} 个建议")
                
                # 创建建议按钮
                for i, suggestion in enumerate(suggestions):
                    btn = ttk.Button(self.suggestion_buttons_frame, text=suggestion,
                                   command=lambda s=suggestion: self._use_suggestion(s))
                    btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
            else:
                # 识别当前命令类型
                cmd_type, params = self.command_recognizer.recognize_command(current_text)
                self.suggestion_label.config(text=f"识别命令类型: {cmd_type.value}")
                
                # 根据命令类型显示相关信息
                if cmd_type == CommandType.DESKTOP_SCAN:
                    self._show_desktop_scan_info()
                elif cmd_type == CommandType.DESKTOP_SEARCH:
                    self._show_desktop_search_info(params)
                elif cmd_type == CommandType.DESKTOP_LAUNCH:
                    self._show_desktop_launch_info(params)
                elif cmd_type == CommandType.WEB_SEARCH:
                    self._show_web_search_info(params)
                elif cmd_type == CommandType.BILIBILI_OPERATION:
                    self._show_bilibili_info(params)
                
        except Exception as e:
            print(f"[ERROR] 更新命令建议时出错: {e}")
    
    def _use_suggestion(self, suggestion):
        """使用建议命令"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", suggestion)
        self.input_text.focus()
    
    def _show_desktop_scan_info(self):
        """显示桌面扫描信息"""
        info_btn = ttk.Button(self.suggestion_buttons_frame, text="📁 扫描桌面文件",
                            command=lambda: self._quick_scan_desktop())
        info_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
    
    def _show_desktop_search_info(self, params):
        """显示桌面搜索信息"""
        keyword = params.get('keyword', '')
        if keyword:
            search_btn = ttk.Button(self.suggestion_buttons_frame, text=f"🔍 搜索 '{keyword}'",
                                  command=lambda: self._quick_search_files())
            search_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
    
    def _show_desktop_launch_info(self, params):
        """显示桌面启动信息"""
        filename = params.get('filename', '')
        if filename:
            launch_btn = ttk.Button(self.suggestion_buttons_frame, text=f"🚀 启动 '{filename}'",
                                  command=lambda: self._quick_launch_file())
            launch_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
    
    def _show_web_search_info(self, params):
        """显示网络搜索信息"""
        keyword = params.get('keyword', '')
        if keyword:
            web_btn = ttk.Button(self.suggestion_buttons_frame, text=f"🌐 搜索 '{keyword}'",
                               command=lambda: self._quick_web_search(keyword))
            web_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
    
    def _show_bilibili_info(self, params):
        """显示B站操作信息"""
        action = params.get('action', '')
        if action == 'search_play':
            keyword = params.get('keyword', '')
            if keyword:
                bili_btn = ttk.Button(self.suggestion_buttons_frame, text=f"📺 播放 '{keyword}'",
                                    command=lambda: self._quick_bilibili_play(keyword))
                bili_btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
    
    def _quick_web_search(self, keyword):
        """快速网络搜索"""
        self.add_to_chat("系统", f"正在搜索网络信息: {keyword}", "info")
        if self.agent:
            threading.Thread(target=self._run_desktop_command, args=(f"搜索网络信息 {keyword}",), daemon=True).start()
    
    def _quick_bilibili_play(self, keyword):
        """快速B站播放"""
        self.add_to_chat("系统", f"正在B站搜索播放: {keyword}", "info")
        if self.agent:
            threading.Thread(target=self._run_desktop_command, args=(f"B站搜索播放 {keyword}",), daemon=True).start()
    
    def _quick_search_files(self):
        """快速搜索文件"""
        keyword = tk.simpledialog.askstring("搜索桌面文件", "请输入搜索关键词：", parent=self.root)
        if keyword:
            self.add_to_chat("系统", f"正在搜索包含 '{keyword}' 的文件...", "info")
            if self.agent:
                threading.Thread(target=self._run_desktop_command, args=(f"搜索桌面文件 {keyword}",), daemon=True).start()
    
    def _quick_launch_file(self):
        """快速启动文件"""
        filename = tk.simpledialog.askstring("启动桌面文件", "请输入文件名：", parent=self.root)
        if filename:
            self.add_to_chat("系统", f"正在启动 '{filename}'...", "info")
            if self.agent:
                threading.Thread(target=self._run_desktop_command, args=(f"启动桌面文件 {filename}",), daemon=True).start()

    
    def send_message(self):
        """发送消息"""
        if not self.agent:
            messagebox.showerror("错误", "LAM Agent 未初始化")
            return
            
        question = self.input_text.get("1.0", tk.END).strip()
        if not question:
            return
        
        # 识别命令类型
        cmd_type, params = self.command_recognizer.recognize_command(question)
        
        # 添加到对话历史
        self.conversation_history.append({"type": "user", "content": question})
        self.update_history_list()
        
        # 显示用户消息
        self.add_to_chat("用户", question, "user")
        
        # 显示识别的命令类型
        self.add_to_chat("系统", f"识别命令类型: {cmd_type.value}", "info")
        if params:
            self.add_to_chat("系统", f"命令参数: {params}", "info")
        
        # 禁用发送按钮
        self.send_button.configure(state=tk.DISABLED)
        self.status_var.set("处理中...")
        
        # 根据命令类型选择处理方式
        if cmd_type in [CommandType.DESKTOP_SCAN, CommandType.DESKTOP_SEARCH, CommandType.DESKTOP_LAUNCH]:
            # 桌面操作直接处理
            thread = threading.Thread(target=self.process_desktop_command, args=(question, cmd_type, params))
        else:
            # 其他操作使用LAM Agent处理
            thread = threading.Thread(target=self.process_message, args=(question,))
        
        thread.daemon = True
        thread.start()
    
    def process_desktop_command(self, question: str, cmd_type: CommandType, params: Dict[str, Any]):
        """处理桌面命令"""
        try:
            from src.tools.desktop_integration import DesktopIntegration
            integration = DesktopIntegration()
            
            if cmd_type == CommandType.DESKTOP_SCAN:
                result = integration.scan_desktop()
                self._handle_desktop_result(result, "扫描桌面文件")
                
            elif cmd_type == CommandType.DESKTOP_SEARCH:
                keyword = params.get('keyword', '')
                if keyword:
                    result = integration.search_desktop(f"搜索桌面 {keyword}")
                    self._handle_desktop_result(result, f"搜索桌面文件: {keyword}")
                else:
                    self.add_to_chat("系统", "未找到搜索关键词", "warning")
                    
            elif cmd_type == CommandType.DESKTOP_LAUNCH:
                filename = params.get('filename', '')
                if filename:
                    result = integration.launch_from_command(f"启动 {filename}")
                    self._handle_desktop_result(result, f"启动桌面文件: {filename}")
                else:
                    self.add_to_chat("系统", "未找到文件名", "warning")
            
            # 清空输入框
            self.root.after(0, self.clear_input)
            
        except Exception as e:
            self.add_to_chat("系统", f"桌面操作失败: {str(e)}", "error")
        finally:
            # 恢复UI状态
            self.root.after(0, self.reset_ui_state)
    
    def _handle_desktop_result(self, result: Dict[str, Any], operation: str):
        """处理桌面操作结果"""
        if result.get('success'):
            self.add_to_chat("系统", f"[SUCCESS] {operation} 成功", "success")
            
            # 显示详细信息
            if 'files' in result and result['files']:
                files = result['files']
                self.add_to_chat("系统", f"找到 {len(files)} 个文件/快捷方式:", "info")
                
                for i, file_info in enumerate(files[:10], 1):  # 只显示前10个
                    file_type = "[SHORTCUT]" if file_info.get('type') == 'shortcut' else "[FILE]"
                    executable = "[EXE]" if file_info.get('executable') else ""
                    self.add_to_chat("系统", f"{i:2d}. {file_type} {file_info['name']} {executable}", "info")
                    if file_info.get('description'):
                        self.add_to_chat("系统", f"     {file_info['description']}", "info")
                
                if len(files) > 10:
                    self.add_to_chat("系统", f"... 还有 {len(files) - 10} 个文件", "info")
            
            # 显示启动信息
            if 'launch_result' in result:
                launch_result = result['launch_result']
                if launch_result.get('success'):
                    self.add_to_chat("系统", "[SUCCESS] 启动成功!", "success")
                    if launch_result.get('process_id'):
                        self.add_to_chat("系统", f"进程ID: {launch_result['process_id']}", "info")
                else:
                    self.add_to_chat("系统", f"[ERROR] 启动失败: {launch_result.get('error', '未知错误')}", "error")
        else:
            self.add_to_chat("系统", f"[ERROR] {operation} 失败: {result.get('error', '未知错误')}", "error")
    
    def process_message(self, question: str):
        """处理消息"""
        try:
            # 调用LAM Agent
            result = self.agent.run(question)
            
            # 添加到对话历史
            self.conversation_history.append({"type": "ai", "content": result['answer']})
            self.update_history_list()
            
            # 显示AI回答
            self.add_to_chat("AI", result['answer'], "ai")
            
            # 显示元信息
            if result.get('sources'):
                self.add_to_chat("系统", "来源链接:", "info")
                for i, source in enumerate(result['sources'], 1):
                    if source:
                        self.add_to_chat("系统", f"{i}. {source}", "info")
            
            # 显示执行计划
            plan_text = f"执行计划: {result['plan']}"
            if "search" in result['plan']:
                plan_text += " (网络搜索)"
            elif "browse:" in result['plan']:
                plan_text += " (网页抓取)"
            elif "execute:" in result['plan']:
                plan_text += " (直接操作)"
            else:
                plan_text += " (直接回答)"
            
            self.add_to_chat("系统", plan_text, "info")
            self.add_to_chat("系统", f"证据数量: {result['evidence_count']}", "info")
            
            # 如果是搜索操作，显示搜索状态
            if "search" in result['plan']:
                if result['evidence_count'] > 0:
                    self.add_to_chat("系统", f"搜索成功，找到 {result['evidence_count']} 个结果", "success")
                    # 检查是否有浏览器搜索
                    browser_search_found = False
                    for evidence in result.get('evidence', []):
                        if "浏览器搜索" in evidence.get('title', ''):
                            browser_search_found = True
                            self.add_to_chat("系统", "已在浏览器中打开多个搜索引擎页面", "success")
                            break
                    if not browser_search_found:
                        self.add_to_chat("系统", "程序化搜索完成，结果已整合到回答中", "info")
                else:
                    self.add_to_chat("系统", "搜索未找到结果，使用AI知识库回答", "warning")
            
            # 清空输入框
            self.root.after(0, self.clear_input)
            
        except Exception as e:
            self.add_to_chat("系统", f"错误: {str(e)}", "error")
        
        finally:
            # 恢复UI状态
            self.root.after(0, self.reset_ui_state)
    
    def add_to_chat(self, sender: str, message: str, tag: str = "normal"):
        """添加消息到聊天区域"""
        def _add():
            self.chat_text.configure(state=tk.NORMAL)
            
            # 添加时间戳
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # 添加发送者
            self.chat_text.insert(tk.END, f"{sender}: ", tag)
            
            # 添加消息内容
            self.chat_text.insert(tk.END, f"{message}\n\n", tag)
            
            self.chat_text.configure(state=tk.DISABLED)
            self.chat_text.see(tk.END)
        
        self.root.after(0, _add)
    
    def clear_input(self):
        """清空输入框"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.focus()
    
    def clear_conversation(self):
        """清空对话"""
        if messagebox.askyesno("确认", "确定要清空所有对话吗？"):
            self.chat_text.configure(state=tk.NORMAL)
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.configure(state=tk.DISABLED)
            self.conversation_history.clear()
            self.update_history_list()
    
    def reset_ui_state(self):
        """重置UI状态"""
        self.send_button.configure(state=tk.NORMAL)
        self.status_var.set("就绪")
    
    def update_history_list(self):
        """更新历史列表"""
        self.history_listbox.delete(0, tk.END)
        for i, item in enumerate(self.conversation_history[-10:]):  # 只显示最近10条
            preview = item['content'][:50] + "..." if len(item['content']) > 50 else item['content']
            self.history_listbox.insert(tk.END, f"{i+1}. {preview}")
    
    def load_history_item(self):
        """加载历史项目"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.conversation_history):
                item = self.conversation_history[-(10-index)]
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", item['content'])
                self.input_text.focus()
    
    def delete_history_item(self):
        """删除历史项目"""
        selection = self.history_listbox.curselection()
        if selection:
            if messagebox.askyesno("确认", "确定要删除这条历史记录吗？"):
                index = selection[0]
                if index < len(self.conversation_history):
                    del self.conversation_history[-(10-index)]
                    self.update_history_list()
    
    def new_conversation(self):
        """新建对话"""
        self.clear_conversation()
    
    def save_conversation(self):
        """保存对话"""
        if not self.conversation_history:
            messagebox.showwarning("警告", "没有对话内容可保存")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", "对话已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def load_conversation(self):
        """加载对话"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                
                # 清空并重新显示对话
                self.chat_text.configure(state=tk.NORMAL)
                self.chat_text.delete("1.0", tk.END)
                self.chat_text.configure(state=tk.DISABLED)
                
                for item in self.conversation_history:
                    self.add_to_chat("用户" if item['type'] == 'user' else "AI", 
                                   item['content'], item['type'])
                
                self.update_history_list()
                messagebox.showinfo("成功", "对话已加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def export_logs(self):
        """导出日志"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.chat_text.get("1.0", tk.END))
                messagebox.showinfo("成功", "日志已导出")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def copy_selected(self):
        """复制选中文本"""
        try:
            selected = self.chat_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass
    
    def select_all(self):
        """全选"""
        self.chat_text.tag_add(tk.SEL, "1.0", tk.END)
        self.chat_text.mark_set(tk.INSERT, "1.0")
        self.chat_text.see(tk.INSERT)
    
    def test_connection(self):
        """测试连接"""
        if self.agent:
            try:
                result = self.agent.run("测试连接")
                messagebox.showinfo("成功", "连接测试成功！")
            except Exception as e:
                messagebox.showerror("失败", f"连接测试失败: {str(e)}")
        else:
            messagebox.showerror("错误", "Agent未初始化")
    
    def view_logs(self):
        """查看日志"""
        log_window = tk.Toplevel(self.root)
        log_window.title("系统日志")
        log_window.geometry("800x500")
        
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 读取日志文件
        try:
            log_dir = os.path.join(project_root, "logs")
            log_file = os.path.join(log_dir, "app.log")
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_text.insert(tk.END, f.read())
            else:
                log_text.insert(tk.END, "未找到日志文件。\n")
        except Exception as e:
            log_text.insert(tk.END, f"读取日志失败: {e}\n")
    
    def open_config(self):
        """打开配置对话框"""
        try:
            config_window = ConfigWindow(self.root, self)
            # 某些环境自定义窗口不具备grab_set，做安全调用
            if hasattr(config_window, 'grab_set'):
                config_window.grab_set()
            elif hasattr(config_window, 'window') and hasattr(config_window.window, 'grab_set'):
                config_window.window.grab_set()
        except Exception as e:
            messagebox.showwarning("配置", f"打开配置窗口时发生问题：{e}\n已忽略模态设置，窗口仍可使用。")
    
    def show_help(self):
        """显示帮助"""
        help_text = """LAM-Agent Pro 使用说明

1. 基本功能：
   - 在输入框中输入问题
   - 点击发送按钮或按Ctrl+Enter
   - AI会给出详细回答

2. 桌面操作：
   - 扫描桌面文件：查看桌面上的所有文件
   - 搜索文件：根据关键词搜索桌面文件
   - 启动文件：启动桌面上的应用程序
   - 桌面管理：打开完整的桌面管理界面

3. 快速操作：
   - 使用侧边栏的快速按钮
   - 选择预设的问题类型
   - 桌面操作按钮

4. 对话管理：
   - 保存和加载对话历史
   - 导出对话日志
   - 清空对话内容

5. 快捷键：
   - Ctrl+Enter: 发送消息
   - Ctrl+A: 全选
   - Ctrl+C: 复制

6. 配置选项：
   - 修改API设置
   - 选择不同模型
   - 调整浏览器模式

7. 桌面命令示例：
   - "扫描桌面文件"
   - "搜索桌面文件 python"
   - "启动桌面文件 文件名" """
        
        messagebox.showinfo("使用说明", help_text)
    
    def show_shortcuts(self):
        """显示快捷键"""
        shortcuts = """快捷键列表：

Ctrl+Enter    发送消息
Ctrl+A        全选文本
Ctrl+C        复制选中文本
Ctrl+V        粘贴文本
F5            刷新界面
Ctrl+N        新建对话
Ctrl+S        保存对话
Ctrl+O        加载对话
Ctrl+E        导出日志"""
        
        messagebox.showinfo("快捷键", shortcuts)
    
    def show_about(self):
        """显示关于"""
        about_text = """LAM-Agent Pro v2.0

基于 DeepSeek 大语言模型的智能助手
支持网络搜索和网页抓取功能

主要特性：
• 智能对话
• 网络搜索
• 网页抓取
• 对话管理
• 历史记录
• 配置管理

开发者: LAM-Agent Team
模型: DeepSeek-Chat
界面: Tkinter"""
        
        messagebox.showinfo("关于", about_text)


class ConfigWindow:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.window = tk.Toplevel(parent)
        self.window.title("配置设置")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        self.setup_config_ui()
    
    def setup_config_ui(self):
        """设置配置界面"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # API配置标签页
        api_frame = ttk.Frame(notebook, padding="10")
        notebook.add(api_frame, text="API配置")
        
        # API Key
        ttk.Label(api_frame, text="DeepSeek API Key:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_var = tk.StringVar(value=os.getenv('DEEPSEEK_API_KEY', ''))
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 模型选择
        ttk.Label(api_frame, text="模型:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.model_var = tk.StringVar(value=os.getenv('LAM_AGENT_MODEL', 'deepseek-chat'))
        model_combo = ttk.Combobox(api_frame, textvariable=self.model_var, 
                                  values=['deepseek-chat', 'deepseek-coder', 'gpt-4o-mini', 'gpt-4'])
        model_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 界面配置标签页
        ui_frame = ttk.Frame(notebook, padding="10")
        notebook.add(ui_frame, text="界面配置")
        
        # 主题选择
        ttk.Label(ui_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.theme_var = tk.StringVar(value="default")
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var, 
                                  values=['default', 'dark', 'light'])
        theme_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 字体大小
        ttk.Label(ui_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.font_size_var = tk.StringVar(value="11")
        font_size_combo = ttk.Combobox(ui_frame, textvariable=self.font_size_var, 
                                      values=['9', '10', '11', '12', '14', '16'])
        font_size_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="保存", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.LEFT)
    
    def save_config(self):
        """保存配置"""
        try:
            # 更新环境变量
            os.environ['DEEPSEEK_API_KEY'] = self.api_key_var.get()
            os.environ['LAM_AGENT_MODEL'] = self.model_var.get()
            
            # 重新初始化Agent
            self.main_app.setup_agent()
            
            messagebox.showinfo("成功", "配置已保存并应用")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = LAMAgentUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
