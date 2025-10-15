#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAM-Agent ChatGPT风格UI
现代化、简洁、优雅的界面设计
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
import os
import sys
import time
from typing import Optional, Dict, Any, List
import json
import webbrowser
from datetime import datetime
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.agent.lam_agent import LamAgent
from src.tools.executor import executor
from src.tools.command_recognizer import CommandRecognizer, CommandType
from src.database.credential_db import credential_db

logger = logging.getLogger(__name__)

class ChatGPTUI:
    """ChatGPT风格的LAM-Agent界面"""
    
    def __init__(self, root):
        self.root = root
        self.agent: Optional[LamAgent] = None
        self.conversation_history = []
        self.command_recognizer = CommandRecognizer()
        self.current_view = "main"  # "main" 或 "credentials"
        
        # ChatGPT风格配色方案
        self.colors = {
            # 主色调
            'bg_main': '#212121',           # 主背景色（更深）
            'bg_sidebar': '#171717',        # 侧边栏背景色
            'bg_input': '#2F2F2F',          # 输入框背景色
            'bg_card': '#2A2A2A',           # 卡片背景色
            'bg_hover': '#3A3A3A',          # 悬停背景色
            
            # 文字颜色
            'text_primary': '#FFFFFF',       # 主要文字颜色
            'text_secondary': '#B3B3B3',     # 次要文字颜色
            'text_muted': '#808080',         # 静音文字颜色
            'text_accent': '#10A37F',        # 强调文字颜色
            
            # 功能色
            'accent': '#10A37F',             # 主要强调色
            'accent_hover': '#0D8F6B',       # 强调色悬停
            'accent_light': '#4FD1C7',       # 浅强调色
            'success': '#10A37F',            # 成功色
            'warning': '#FF9500',            # 警告色
            'error': '#FF3B30',              # 错误色
            'info': '#007AFF',               # 信息色
            
            # 边框和分割线
            'border': '#404040',             # 边框颜色
            'border_light': '#333333',        # 浅边框颜色
            'separator': '#2A2A2A',          # 分割线颜色
            
            # 特殊效果
            'shadow': '#000000',              # 阴影色
            'glass': '#FFFFFF10',             # 玻璃效果色
        }
        
        self.setup_ui()
        self.setup_agent()
        
    def setup_ui(self):
        """设置ChatGPT风格用户界面"""
        self.root.title("LAM-Agent Pro")
        self.root.geometry("1600x1000")
        self.root.configure(bg=self.colors['bg_main'])
        self.root.minsize(1200, 800)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 全局快捷键：快速返回对话
        try:
            self.root.bind('<Alt-Left>', lambda e: self.show_main_interface())
            self.root.bind('<Control-1>', lambda e: self.show_main_interface())
            # 快速打开凭据管理
            self.root.bind('<Alt-c>', lambda e: self.show_credential_interface())
            self.root.bind('<Control-2>', lambda e: self.show_credential_interface())
        except Exception:
            pass

        # 应用统一样式
        self.apply_styles()
        
        # 创建主布局
        self.create_main_layout()
        
        # 创建侧边栏
        self.create_sidebar()
        
        # 创建主内容区域
        self.create_main_content()
        
        # 创建底部输入区域
        self.create_input_area()
        
        # 默认显示主界面
        self.show_main_interface()
        
    def create_main_layout(self):
        """创建主布局"""
        # 主容器
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
    def create_sidebar(self):
        """创建侧边栏"""
        # 侧边栏容器
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['bg_sidebar'], width=240)
        self.sidebar.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # 顶部Logo区域
        self.create_sidebar_header()
        
        # 功能按钮区域
        self.create_sidebar_buttons()
        
        # 对话历史区域
        self.create_sidebar_history()
        
        # 底部设置区域
        self.create_sidebar_footer()
        
    def create_sidebar_header(self):
        """创建侧边栏头部"""
        header_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        # Logo和标题
        logo_frame = tk.Frame(header_frame, bg=self.colors['bg_sidebar'])
        logo_frame.pack(fill=tk.X)
        
        # Logo图标
        logo_label = tk.Label(logo_frame, text="🤖", font=('Arial', 24), 
                             bg=self.colors['bg_sidebar'], fg=self.colors['accent'])
        logo_label.pack(anchor=tk.W)
        
        # 标题
        title_label = tk.Label(logo_frame, text="LAM-Agent Pro", 
                              font=('Arial', 16, 'bold'),
                              bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        title_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 副标题
        subtitle_label = tk.Label(logo_frame, text="智能桌面助手", 
                                 font=('Arial', 10),
                                 bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor=tk.W)
        
    def create_sidebar_buttons(self):
        """创建侧边栏功能按钮"""
        buttons_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 功能按钮
        self.buttons = {}
        button_configs = [
            ("↩ 返回对话", self.show_main_interface, "back"),
            ("💬 新对话", self.new_conversation, "main"),
            ("🔐 凭据管理", self.show_credential_interface, "credentials"),
            ("🛠️ 工具面板", self.show_tools_panel, "tools"),
            ("⚙️ 设置", self.show_settings, "settings"),
        ]
        
        for text, command, view_type in button_configs:
            btn = tk.Button(buttons_frame, text=text, command=command,
                           bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'],
                           font=('Arial', 12), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['bg_hover'],
                           activeforeground=self.colors['text_primary'],
                           cursor='hand2', anchor=tk.W, padx=15, pady=12)
            btn.pack(fill=tk.X, pady=2)
            self.buttons[view_type] = btn
        
        # 分隔线
        separator = tk.Frame(buttons_frame, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, pady=15)
        
    def create_sidebar_history(self):
        """创建侧边栏对话历史"""
        history_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 历史标题
        history_title = tk.Label(history_frame, text="💬 对话历史", 
                                font=('Arial', 12, 'bold'),
                                bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        history_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 历史列表容器
        history_container = tk.Frame(history_frame, bg=self.colors['bg_sidebar'])
        history_container.pack(fill=tk.BOTH, expand=True)
        
        # 历史列表
        self.history_listbox = tk.Listbox(history_container, 
                                         bg=self.colors['bg_input'], 
                                         fg=self.colors['text_primary'], 
                                         font=('Arial', 10),
                                         selectbackground=self.colors['bg_hover'],
                                         selectforeground=self.colors['text_primary'],
                                         relief=tk.FLAT, bd=0,
                                         highlightthickness=0)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 绑定选择事件
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)
        
    def create_sidebar_footer(self):
        """创建侧边栏底部"""
        footer_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'], height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=20)
        footer_frame.pack_propagate(False)
        
        # 状态标签
        self.status_label = tk.Label(footer_frame, text="就绪", 
                                    bg=self.colors['bg_sidebar'], 
                                    fg=self.colors['text_secondary'],
                                    font=('Arial', 10))
        self.status_label.pack(anchor=tk.W)
        
        # 时间标签
        self.time_label = tk.Label(footer_frame, text="", 
                                  bg=self.colors['bg_sidebar'], 
                                  fg=self.colors['text_muted'],
                                  font=('Arial', 9))
        self.time_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 更新时间
        self.update_time()
        
    def create_main_content(self):
        """创建主内容区域"""
        # 主内容容器
        self.content_frame = tk.Frame(self.main_container, bg=self.colors['bg_main'])
        self.content_frame.grid(row=0, column=1, sticky='nsew', padx=0, pady=0)
        
        # 创建主界面
        self.create_main_interface()
        
        # 创建凭据管理器界面
        self.create_credential_interface()
        
        # 创建工具面板界面
        self.create_tools_interface()
        
        # 创建设置界面
        self.create_settings_interface()
        
    def create_main_interface(self):
        """创建主界面"""
        self.main_interface = tk.Frame(self.content_frame, bg=self.colors['bg_main'])
        
        # 聊天区域容器
        chat_container = tk.Frame(self.main_interface, bg=self.colors['bg_main'])
        chat_container.pack(fill=tk.BOTH, expand=True, padx=48, pady=36)
        
        # 聊天标题和状态
        title_frame = tk.Frame(chat_container, bg=self.colors['bg_main'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        chat_title = tk.Label(title_frame, text="💬 与 LAM-Agent 对话", 
                             font=('Arial', 18, 'bold'),
                             bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        chat_title.pack(side=tk.LEFT)
        
        # 执行状态指示器
        self.execution_status = tk.Label(title_frame, text="", 
                                       font=('Arial', 10),
                                       bg=self.colors['bg_main'], fg=self.colors['accent'])
        self.execution_status.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress_frame = tk.Frame(chat_container, bg=self.colors['bg_main'])
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', 
                                          style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X)
        self.progress_frame.pack_forget()  # 初始隐藏
        
        # 聊天文本区域
        self.chat_text = scrolledtext.ScrolledText(
            chat_container, 
            font=("Arial", 12),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.colors['text_primary'],
            padx=20,
            pady=20
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置文本标签样式
        self.configure_chat_tags()
        
    def configure_chat_tags(self):
        """配置聊天文本标签样式"""
        self.chat_text.tag_configure("user", foreground=self.colors['accent'], font=("Arial", 12, "bold"))
        self.chat_text.tag_configure("ai", foreground=self.colors['text_primary'], font=("Arial", 12))
        self.chat_text.tag_configure("system", foreground=self.colors['text_secondary'], font=("Arial", 11, "italic"))
        self.chat_text.tag_configure("error", foreground=self.colors['error'], font=("Arial", 12, "bold"))
        self.chat_text.tag_configure("success", foreground="#4CAF50", font=("Arial", 11, "bold"))
        self.chat_text.tag_configure("warning", foreground="#FF9800", font=("Arial", 11, "bold"))
        self.chat_text.tag_configure("info", foreground="#2196F3", font=("Arial", 11))
        self.chat_text.tag_configure("timestamp", foreground=self.colors['text_muted'], font=("Arial", 9))
        
    def create_input_area(self):
        """创建输入区域"""
        # 输入区域容器
        self.input_container = tk.Frame(self.main_container, bg=self.colors['bg_main'], height=120)
        self.input_container.grid(row=1, column=0, columnspan=2, sticky='ew', padx=0, pady=0)
        self.input_container.grid_propagate(False)
        
        # 输入区域内容
        input_content = tk.Frame(self.input_container, bg=self.colors['bg_card'])
        input_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # 输入框容器
        input_frame = tk.Frame(input_content, bg=self.colors['bg_card'])
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入文本框
        self.input_text = tk.Text(input_frame, height=3, wrap=tk.WORD, 
                                 font=("Arial", 12), bg=self.colors['bg_input'],
                                 fg=self.colors['text_primary'], relief=tk.FLAT, bd=0,
                                 insertbackground=self.colors['text_primary'],
                                 padx=15, pady=10)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # 发送按钮
        send_btn = tk.Button(input_frame, text="📤", command=self.send_message,
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           font=('Arial', 16), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['accent_hover'],
                           cursor='hand2', width=3, height=2)
        send_btn.pack(side=tk.RIGHT)
        
        # 绑定快捷键
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
        self.input_text.bind('<KeyRelease>', self.on_input_change)
        
        # 占位符文本
        self.input_text.insert(1.0, "输入消息...")
        self.input_text.config(fg=self.colors['text_muted'])
        self.input_text.bind('<FocusIn>', self.on_input_focus_in)
        self.input_text.bind('<FocusOut>', self.on_input_focus_out)
        
    def create_credential_interface(self):
        """创建凭据管理器界面"""
        self.credential_interface = tk.Frame(self.content_frame, bg=self.colors['bg_main'])
        
        # 顶部标题栏
        title_frame = tk.Frame(self.credential_interface, bg=self.colors['bg_main'], height=80)
        title_frame.pack(fill=tk.X, padx=40, pady=20)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🔐 凭据管理器", 
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        title_label.pack(anchor=tk.W)

        # 顶部操作工具栏（显眼位置）
        toolbar = tk.Frame(self.credential_interface, bg=self.colors['bg_main'])
        toolbar.pack(fill=tk.X, padx=40, pady=(0, 10))

        def toolbar_btn(text, cmd, bg, active_bg):
            return tk.Button(toolbar, text=text, command=cmd,
                             bg=bg, fg=self.colors['text_primary'], font=('Arial', 11),
                             relief=tk.FLAT, bd=0, activebackground=active_bg,
                             cursor='hand2', padx=14, pady=6)

        toolbar_btn("➕ 新增", self.add_credential, self.colors['accent'], self.colors['accent_hover']).pack(side=tk.LEFT, padx=(0, 8))
        toolbar_btn("✏️ 修改", self.edit_credential, self.colors['warning'], '#E6940A').pack(side=tk.LEFT, padx=8)
        toolbar_btn("💾 保存", self.save_credential, self.colors['bg_input'], self.colors['bg_hover']).pack(side=tk.LEFT, padx=8)
        toolbar_btn("🗑️ 删除", self.delete_credential, self.colors['error'], '#E55A5A').pack(side=tk.LEFT, padx=8)
        
        # 主内容区域
        content_frame = tk.Frame(self.credential_interface, bg=self.colors['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))
        
        # 左侧凭据列表
        self.create_credential_list(content_frame)
        
        # 右侧凭据详情
        self.create_credential_details(content_frame)
        
    def create_credential_list(self, parent):
        """创建凭据列表"""
        # 左侧框架
        left_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # 搜索区域
        search_frame = tk.Frame(left_frame, bg=self.colors['bg_card'])
        search_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 搜索框
        search_label = tk.Label(search_frame, text="🔍 搜索凭据", 
                               font=('Arial', 12, 'bold'),
                               bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        search_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                   bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                                   font=('Arial', 11), relief=tk.FLAT, bd=0,
                                   insertbackground=self.colors['text_primary'])
        self.search_entry.pack(fill=tk.X, pady=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_credential_search)
        
        # 凭据列表
        list_frame = tk.Frame(left_frame, bg=self.colors['bg_card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 列表标题
        list_title = tk.Label(list_frame, text="📋 凭据列表", 
                             font=('Arial', 12, 'bold'),
                             bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        list_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 创建Treeview（移除“用户名”列）
        columns = ('应用', '账号')
        self.credential_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # 设置列标题和宽度
        column_widths = {'应用': 100, '账号': 160}
        for col in columns:
            self.credential_tree.heading(col, text=col)
            self.credential_tree.column(col, width=column_widths[col])
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.credential_tree.yview)
        self.credential_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.credential_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.credential_tree.bind('<<TreeviewSelect>>', self.on_credential_select)
        
    def create_credential_details(self, parent):
        """创建凭据详情"""
        # 右侧框架
        right_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 详情标题
        detail_title = tk.Label(right_frame, text="📝 凭据详情", 
                               font=('Arial', 16, 'bold'),
                               bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        detail_title.pack(anchor=tk.W, padx=20, pady=20)
        
        # 表单容器
        form_container = tk.Frame(right_frame, bg=self.colors['bg_card'])
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 表单字段
        # 表单字段（移除用户名）
        fields = [
            ('账号', 'account'),
            ('密码', 'password'),
            ('应用', 'application'),
            ('联系方式', 'contact'),
            ('网站URL', 'website_url'),
            ('备注', 'notes')
        ]
        
        self.form_vars = {}
        self.form_entries = {}
        
        for i, (label, field) in enumerate(fields):
            # 创建字段容器
            field_frame = tk.Frame(form_container, bg=self.colors['bg_card'])
            field_frame.pack(fill=tk.X, pady=15)
            
            # 标签
            label_widget = tk.Label(field_frame, text=f"{label}:", 
                                   font=('Arial', 12, 'bold'),
                                   bg=self.colors['bg_card'], fg=self.colors['text_primary'])
            label_widget.pack(anchor=tk.W, pady=(0, 5))
            
            # 输入框
            if field == 'password':
                # 密码框
                self.form_vars[field] = tk.StringVar()
                self.form_entries[field] = tk.Entry(field_frame, textvariable=self.form_vars[field], 
                                                   show='*', bg=self.colors['bg_input'], 
                                                   fg=self.colors['text_primary'],
                                                   font=('Arial', 11), relief=tk.FLAT, bd=0,
                                                   insertbackground=self.colors['text_primary'])
            elif field == 'notes':
                # 备注使用文本框
                self.form_vars[field] = tk.StringVar()
                self.form_entries[field] = tk.Text(field_frame, height=4, bg=self.colors['bg_input'], 
                                                  fg=self.colors['text_primary'],
                                                  font=('Arial', 11), relief=tk.FLAT, bd=0,
                                                  insertbackground=self.colors['text_primary'])
            else:
                # 普通输入框
                self.form_vars[field] = tk.StringVar()
                self.form_entries[field] = tk.Entry(field_frame, textvariable=self.form_vars[field],
                                                   bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                                                   font=('Arial', 11), relief=tk.FLAT, bd=0,
                                                   insertbackground=self.colors['text_primary'])
            
            self.form_entries[field].pack(fill=tk.X, pady=(0, 5))
        
        # 操作按钮
        button_frame = tk.Frame(form_container, bg=self.colors['bg_card'])
        button_frame.pack(fill=tk.X, pady=20)

        def make_btn(parent, text, cmd, bg, active_bg, pad=(0, 10)):
            btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg=self.colors['text_primary'],
                            font=('Arial', 12), relief=tk.FLAT, bd=0, activebackground=active_bg,
                            cursor='hand2', padx=16, pady=8)
            btn.pack(side=tk.LEFT, padx=pad)
            return btn

        # 基本CRUD
        make_btn(button_frame, "➕ 添加", self.add_credential, self.colors['accent'], self.colors['accent_hover'], (0, 10))
        make_btn(button_frame, "✏️ 修改", self.edit_credential, self.colors['warning'], '#E6940A', (0, 10))
        make_btn(button_frame, "💾 保存", self.save_credential, self.colors['bg_input'], self.colors['bg_hover'], (0, 20))
        make_btn(button_frame, "🗑️ 删除", self.delete_credential, self.colors['error'], '#E55A5A', (0, 20))

        # 快捷操作
        quick_frame = tk.Frame(form_container, bg=self.colors['bg_card'])
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        make_btn(quick_frame, "📋 复制账号", lambda: self.copy_field_to_clipboard('account'), self.colors['bg_input'], self.colors['bg_hover'])
        make_btn(quick_frame, "🔑 复制密码", lambda: self.copy_field_to_clipboard('password'), self.colors['bg_input'], self.colors['bg_hover'])
        make_btn(quick_frame, "🌐 打开网站", self.open_credential_website, self.colors['bg_input'], self.colors['bg_hover'])
        
        # 当前选中的凭据ID
        self.current_credential_id = None
        
    def create_tools_interface(self):
        """创建工具面板界面"""
        self.tools_interface = tk.Frame(self.content_frame, bg=self.colors['bg_main'])
        
        # 工具面板内容
        tools_content = tk.Frame(self.tools_interface, bg=self.colors['bg_main'])
        tools_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 工具标题
        tools_title = tk.Label(tools_content, text="🛠️ 工具面板", 
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        tools_title.pack(anchor=tk.W, pady=(0, 30))
        
        # 工具网格
        tools_grid = tk.Frame(tools_content, bg=self.colors['bg_main'])
        tools_grid.pack(fill=tk.BOTH, expand=True)
        
        # 工具按钮
        tools = [
            ("🔍 桌面扫描", self.scan_desktop, "扫描桌面文件和快捷方式"),
            ("🚀 启动文件", self.launch_file, "启动桌面应用程序"),
            ("🌐 网页自动化", self.web_automation, "自动化网页操作"),
            ("📺 B站操作", self.bilibili_operation, "Bilibili视频操作"),
            ("🎮 Steam集成", self.steam_operation, "Steam游戏操作"),
            ("📊 系统信息", self.system_info, "获取系统信息"),
            ("🛍️ 淘宝搜索商品", self.taobao_search_action, "按店铺与关键字搜索商品"),
            ("💳 淘宝购买/加购", self.taobao_buy_action, "在当前商品页下单或加入购物车"),
            ("⚡ 淘宝一键下单", self.taobao_quick_buy_action, "登录→搜店铺→搜商品→下单/加购"),
        ]
        
        for i, (text, command, description) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_frame = tk.Frame(tools_grid, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
            tool_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # 工具按钮
            tool_btn = tk.Button(tool_frame, text=text, command=command,
                               bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                               font=('Arial', 14, 'bold'), relief=tk.FLAT, bd=0,
                               activebackground=self.colors['bg_hover'],
                               activeforeground=self.colors['text_primary'],
                               cursor='hand2', padx=20, pady=20)
            tool_btn.pack(fill=tk.X, padx=20, pady=(20, 10))
            
            # 工具描述
            desc_label = tk.Label(tool_frame, text=description, 
                                 font=('Arial', 10),
                                 bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                                 wraplength=200)
            desc_label.pack(padx=20, pady=(0, 20))
        
        # 配置网格权重
        for i in range(3):
            tools_grid.columnconfigure(i, weight=1)
        for i in range(2):
            tools_grid.rowconfigure(i, weight=1)
        
    def create_settings_interface(self):
        """创建设置界面"""
        self.settings_interface = tk.Frame(self.content_frame, bg=self.colors['bg_main'])
        
        # 设置内容
        settings_content = tk.Frame(self.settings_interface, bg=self.colors['bg_main'])
        settings_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 设置标题
        settings_title = tk.Label(settings_content, text="⚙️ 设置", 
                                 font=('Arial', 20, 'bold'),
                                 bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        settings_title.pack(anchor=tk.W, pady=(0, 30))
        
        # 设置选项
        settings_options = [
            ("🎨 主题设置", "选择界面主题"),
            ("🔧 模型设置", "配置AI模型"),
            ("📁 路径设置", "设置文件路径"),
            ("🔐 安全设置", "安全选项"),
        ]
        
        for text, description in settings_options:
            option_frame = tk.Frame(settings_content, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
            option_frame.pack(fill=tk.X, pady=10)
            
            # 选项标题
            option_title = tk.Label(option_frame, text=text, 
                                   font=('Arial', 14, 'bold'),
                                   bg=self.colors['bg_card'], fg=self.colors['text_primary'])
            option_title.pack(anchor=tk.W, padx=20, pady=(15, 5))
            
            # 选项描述
            option_desc = tk.Label(option_frame, text=description, 
                                  font=('Arial', 10),
                                  bg=self.colors['bg_card'], fg=self.colors['text_secondary'])
            option_desc.pack(anchor=tk.W, padx=20, pady=(0, 15))
        
    def show_main_interface(self):
        """显示主界面"""
        self.current_view = "main"
        self.hide_all_interfaces()
        self.main_interface.pack(fill=tk.BOTH, expand=True)
        self.update_button_states("main")
        
    def show_credential_interface(self):
        """显示凭据管理器界面"""
        self.current_view = "credentials"
        self.hide_all_interfaces()
        self.credential_interface.pack(fill=tk.BOTH, expand=True)
        self.update_button_states("credentials")
        self.refresh_credential_list()
        
    def show_tools_panel(self):
        """显示工具面板"""
        self.current_view = "tools"
        self.hide_all_interfaces()
        self.tools_interface.pack(fill=tk.BOTH, expand=True)
        self.update_button_states("tools")
        
    def show_settings(self):
        """显示设置界面"""
        self.current_view = "settings"
        self.hide_all_interfaces()
        self.settings_interface.pack(fill=tk.BOTH, expand=True)
        self.update_button_states("settings")
    
    # （移除）用户信息界面入口
        
    def hide_all_interfaces(self):
        """隐藏所有界面"""
        self.main_interface.pack_forget()
        self.credential_interface.pack_forget()
        self.tools_interface.pack_forget()
        self.settings_interface.pack_forget()
        if hasattr(self, 'user_interface'):
            self.user_interface.pack_forget()
        
    def update_button_states(self, active_view):
        """更新按钮状态"""
        for view_type, btn in self.buttons.items():
            # 跳过“返回对话”按钮的高亮
            if view_type == "back":
                btn.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
                continue
            if view_type == active_view:
                btn.config(bg=self.colors['accent'], fg=self.colors['text_primary'])
            else:
                btn.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])

    # （移除）用户信息界面

    # 用户信息操作
    # （移除）用户资料查看

    # （移除）昵称编辑

    # （移除）邮箱编辑

    # （移除）导出日志

    # （移除）清理会话
    
    def setup_agent(self):
        """设置智能代理"""
        try:
            self.agent = LamAgent()
            self.append_to_chat("系统", "LAM-Agent Pro 已启动，可以开始对话！", "system")
            self.update_status("智能代理已启动")
        except Exception as e:
            self.append_to_chat("系统", f"启动智能代理失败: {str(e)}", "error")
            self.update_status("智能代理启动失败")
            logger.error(f"启动智能代理失败: {e}")
    
    def send_message(self):
        """发送消息"""
        message = self.input_text.get(1.0, tk.END).strip()
        if not message or message == "输入消息...":
            return
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, "输入消息...")
        self.input_text.config(fg=self.colors['text_muted'])
        
        # 添加到对话历史
        self.conversation_history.append({"role": "user", "content": message})
        self.add_to_history(f"用户: {message}")
        
        # 显示用户消息
        self.append_to_chat("用户", message, "user")
        
        # 更新状态
        self.update_status("正在处理...")
        
        # 在新线程中处理消息
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message):
        """处理消息"""
        try:
            # 首先判断是问答类还是操作类指令
            command_type = self.classify_message(message)
            
            if command_type == "question":
                # 问答类：使用联网搜索回答
                self.root.after(0, lambda: self.append_to_chat("系统", "识别为问答类问题，正在联网搜索...", "info"))
                self.root.after(0, lambda: self.update_status("联网搜索中..."))
                self.handle_question_with_web_search(message)
            else:
                # 操作类：使用DeepSeek拆分和执行命令
                self.root.after(0, lambda: self.append_to_chat("系统", "识别为操作类指令，正在使用DeepSeek分析...", "info"))
                self.root.after(0, lambda: self.update_status("DeepSeek分析中..."))
                self.execute_deepseek_commands(message)
                    
        except Exception as e:
            error_msg = f"处理消息失败: {str(e)}"
            self.root.after(0, lambda: self.append_to_chat("系统", error_msg, "error"))
            self.root.after(0, lambda: self.update_status("处理失败"))
            logger.error(f"处理消息失败: {e}")
    
    def classify_message(self, message):
        """分类消息：判断是问答类还是操作类"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            # 初始化DeepSeek
            llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                temperature=0.1
            )
            
            # 构建分类提示词
            prompt = f"""
请判断以下用户输入是问答类问题还是操作类指令。

用户输入: {message}

判断标准：
- 问答类：询问信息、知识、解释、建议等（如：什么是人工智能？今天天气怎么样？如何学习Python？）
- 操作类：要求执行具体操作、打开应用、搜索内容、点击按钮等（如：打开B站、搜索视频、点击登录按钮）

请只返回以下两个选项之一：
- "question" (问答类)
- "action" (操作类)
"""
            
            # 调用DeepSeek
            response = llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip().lower()
            
            # 解析结果
            if "question" in result:
                return "question"
            elif "action" in result:
                return "action"
            else:
                # 默认根据关键词判断
                question_keywords = ["什么", "怎么", "如何", "为什么", "哪里", "哪个", "多少", "是否", "?", "？", "吗", "呢"]
                action_keywords = ["打开", "搜索", "点击", "执行", "运行", "启动", "关闭", "播放", "下载", "安装"]
                
                if any(keyword in message for keyword in question_keywords):
                    return "question"
                elif any(keyword in message for keyword in action_keywords):
                    return "action"
                else:
                    return "question"  # 默认为问答类
                    
        except Exception as e:
            logger.error(f"消息分类失败: {e}")
            # 默认根据关键词判断
            question_keywords = ["什么", "怎么", "如何", "为什么", "哪里", "哪个", "多少", "是否", "?", "？", "吗", "呢"]
            action_keywords = ["打开", "搜索", "点击", "执行", "运行", "启动", "关闭", "播放", "下载", "安装"]
            
            if any(keyword in message for keyword in question_keywords):
                return "question"
            elif any(keyword in message for keyword in action_keywords):
                return "action"
            else:
                return "question"  # 默认为问答类
    
    def handle_question_with_web_search(self, message):
        """使用联网搜索处理问答类问题"""
        try:
            # 1. 使用DeepSeek生成搜索关键词
            search_keywords = self.generate_search_keywords(message)
            
            if not search_keywords:
                self.root.after(0, lambda: self.append_to_chat("系统", "无法生成有效的搜索关键词", "warning"))
                self.root.after(0, lambda: self.update_status("就绪"))
                return
            
            # 2. 执行网络搜索
            self.root.after(0, lambda: self.append_to_chat("系统", f"搜索关键词: {', '.join(search_keywords)}", "info"))
            search_results = self.perform_web_search(search_keywords)
            
            if not search_results:
                self.root.after(0, lambda: self.append_to_chat("系统", "网络搜索未找到相关信息", "warning"))
                self.root.after(0, lambda: self.update_status("就绪"))
                return
            
            # 3. 使用DeepSeek基于搜索结果生成回答
            self.root.after(0, lambda: self.append_to_chat("系统", f"找到 {len(search_results)} 条相关信息", "info"))
            answer = self.generate_answer_from_search(message, search_results)
            
            # 4. 显示回答
            self.root.after(0, lambda: self.append_to_chat("AI助手", answer, "ai"))
            self.root.after(0, lambda: self.update_status("就绪"))
            
        except Exception as e:
            error_msg = f"联网搜索回答失败: {str(e)}"
            self.root.after(0, lambda: self.append_to_chat("系统", error_msg, "error"))
            self.root.after(0, lambda: self.update_status("搜索失败"))
            logger.error(f"联网搜索回答失败: {e}")
    
    def generate_search_keywords(self, message):
        """使用DeepSeek生成搜索关键词"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            # 初始化DeepSeek
            llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                temperature=0.1
            )
            
            # 构建提示词
            prompt = f"""
请根据以下用户问题生成3-5个最相关的搜索关键词，用于网络搜索获取答案。

用户问题: {message}

要求：
1. 关键词应该简洁明了
2. 能够有效搜索到相关信息
3. 包含问题的核心概念
4. 使用中文关键词

请按照以下格式返回JSON数组：
["关键词1", "关键词2", "关键词3"]

示例：
用户问题: 什么是人工智能？
返回: ["人工智能", "AI定义", "机器学习", "深度学习"]

请只返回JSON数组，不要包含其他文字。
"""
            
            # 调用DeepSeek
            response = llm.invoke([HumanMessage(content=prompt)])
            result_text = response.content.strip()
            
            # 解析JSON
            import json
            try:
                keywords = json.loads(result_text)
                return keywords if isinstance(keywords, list) else []
            except:
                # 如果失败，尝试提取关键词
                import re
                keywords = re.findall(r'"([^"]+)"', result_text)
                return keywords if keywords else [message]
                
        except Exception as e:
            logger.error(f"生成搜索关键词失败: {e}")
            return [message]  # 返回原问题作为关键词
    
    def perform_web_search(self, keywords):
        """执行网络搜索"""
        try:
            from src.tools.executor import executor
            
            # 组合关键词进行搜索
            query = " ".join(keywords)
            
            # 使用执行器进行网络搜索
            result = executor.execute_action("search_web", {"query": query})
            
            if result.get('success'):
                # 解析搜索结果
                search_data = result.get('data', {})
                results = []
                
                # 提取搜索结果
                if isinstance(search_data, dict):
                    # 如果是字典格式，提取相关信息
                    if 'results' in search_data:
                        results = search_data['results']
                    elif 'snippets' in search_data:
                        results = search_data['snippets']
                    else:
                        # 将整个数据作为结果
                        results = [str(search_data)]
                elif isinstance(search_data, list):
                    results = search_data
                else:
                    results = [str(search_data)]
                
                return results
            else:
                logger.error(f"网络搜索失败: {result.get('error', '')}")
                return []
                
        except Exception as e:
            logger.error(f"执行网络搜索失败: {e}")
            return []
    
    def generate_answer_from_search(self, question, search_results):
        """基于搜索结果生成回答"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            # 初始化DeepSeek
            llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                temperature=0.3
            )
            
            # 构建搜索结果文本
            search_text = "\n".join([f"- {result}" for result in search_results[:5]])  # 限制前5条结果
            
            # 构建提示词
            prompt = f"""
请基于以下网络搜索结果，回答用户的问题。

用户问题: {question}

网络搜索结果:
{search_text}

要求：
1. 基于搜索结果提供准确、有用的回答
2. 如果搜索结果不足以回答问题，请说明
3. 回答要简洁明了，重点突出
4. 使用中文回答
5. 可以适当引用搜索结果中的信息

请直接提供回答，不要包含其他格式。
"""
            
            # 调用DeepSeek
            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip()
            
            return answer
            
        except Exception as e:
            logger.error(f"生成回答失败: {e}")
            return f"抱歉，无法基于搜索结果生成回答。错误: {str(e)}"
    
    def show_progress_bar(self, total_steps):
        """显示进度条"""
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar['maximum'] = total_steps
        self.progress_bar['value'] = 0
        self.execution_status.config(text="执行中...")
    
    def update_progress(self, current_step, total_steps):
        """更新进度条"""
        self.progress_bar['value'] = current_step
        self.execution_status.config(text=f"执行中... ({current_step}/{total_steps})")
    
    def hide_progress_bar(self):
        """隐藏进度条"""
        self.progress_frame.pack_forget()
        self.execution_status.config(text="")
    
    def execute_deepseek_commands(self, message):
        """使用DeepSeek拆分和执行命令"""
        try:
            # 1. 使用DeepSeek拆分命令
            command_steps = self.split_commands_with_deepseek(message)
            
            if not command_steps:
                # DeepSeek拆分失败时，使用智能命令识别
                self.root.after(0, lambda: self.append_to_chat("系统", "DeepSeek拆分失败，使用智能命令识别", "warning"))
                command_steps = self.simple_command_recognition(message)
                
                if not command_steps:
                    self.root.after(0, lambda: self.append_to_chat("系统", "未能识别出可执行的命令步骤", "warning"))
                    self.root.after(0, lambda: self.update_status("就绪"))
                    return
            
            # 2. 逐条执行命令
            self.root.after(0, lambda: self.append_to_chat("系统", f"识别出 {len(command_steps)} 个命令步骤", "info"))
            
            # 显示进度条
            self.root.after(0, lambda: self.show_progress_bar(len(command_steps)))
            
            # 添加上下文记忆
            context = {
                "up_name": None,
                "current_url": None,
                "execution_history": []
            }
            
            for i, step in enumerate(command_steps, 1):
                # 更新进度条
                self.root.after(0, lambda idx=i, total=len(command_steps): self.update_progress(idx, total))
                
                # 显示当前步骤
                step_desc = step.get('description', f'步骤 {i}')
                self.root.after(0, lambda s=step_desc, idx=i: self.append_to_chat("系统", f"执行步骤 {idx}: {s}", "info"))
                self.root.after(0, lambda: self.update_status(f"执行步骤 {i}/{len(command_steps)}"))
                
                # 更新上下文
                self.update_context(context, step)
                
                # 执行单个命令步骤
                result = self.execute_single_command(step)
                
                # 记录执行历史
                context["execution_history"].append({
                    "step": i,
                    "action": step.get('action'),
                    "description": step_desc,
                    "result": result
                })
                
                if result.get('success'):
                    self.root.after(0, lambda r=result: self.append_to_chat("系统", f"✓ 步骤执行成功: {r.get('message', '')}", "success"))
                    
                    # 如果是降级执行，提示用户
                    if result.get('fallback'):
                        self.root.after(0, lambda: self.append_to_chat("系统", "⚠️ 使用降级方案，请在浏览器中手动操作", "warning"))
                    elif result.get('partial'):
                        self.root.after(0, lambda: self.append_to_chat("系统", "⚠️ 部分自动化成功，请在浏览器中完成剩余操作", "warning"))
                else:
                    self.root.after(0, lambda r=result: self.append_to_chat("系统", f"✗ 步骤执行失败: {r.get('error', '')}", "error"))
                
                # 短暂延迟，让用户看到执行过程
                time.sleep(1)
            
            # 隐藏进度条
            self.root.after(0, lambda: self.hide_progress_bar())
            self.root.after(0, lambda: self.update_status("所有命令执行完成"))
            
            # 总结执行结果
            success_count = sum(1 for h in context["execution_history"] if h["result"].get('success'))
            total_count = len(context["execution_history"])
            self.root.after(0, lambda: self.append_to_chat("系统", f"执行完成: {success_count}/{total_count} 个步骤成功", "info"))
            
        except Exception as e:
            error_msg = f"命令执行失败: {str(e)}"
            self.root.after(0, lambda: self.append_to_chat("系统", error_msg, "error"))
            self.root.after(0, lambda: self.update_status("执行失败"))
            logger.error(f"命令执行失败: {e}")
    
    def update_context(self, context, step):
        """更新执行上下文"""
        try:
            action = step.get('action')
            params = step.get('params', {})
            
            # 提取UP主名称
            if action in ['bilibili_open_up']:
                up_name = params.get('up_name') or params.get('keyword')
                if up_name:
                    context["up_name"] = up_name
            
            # 记录当前URL
            if action == 'open_website':
                url = params.get('url')
                if url:
                    context["current_url"] = url
                    
        except Exception as e:
            logger.error(f"更新上下文失败: {e}")
    
    def simple_command_recognition(self, message):
        """智能命令识别（当DeepSeek不可用时）"""
        try:
            message_lower = message.lower()
            steps = []
            
            # B站相关命令识别 - 扩展关键词匹配
            if ("b站" in message or "bilibili" in message_lower or 
                "影视飓风" in message or "搜索" in message or 
                "主页" in message or "首页" in message):
                import re
                
                # 提取UP主名称（影视飓风）
                up_name = "影视飓风"  # 默认值
                up_match = re.search(r'(?:搜索|主页|首页|播放|最新|一期)([^，,，。]+?)(?:，|,|$|视频)', message)
                if up_match:
                    up_name = up_match.group(1).strip()
                
                # 如果没有匹配到，尝试其他模式
                if up_name == "影视飓风":
                    # 尝试匹配"影视飓风"这个词
                    if "影视飓风" in message:
                        up_name = "影视飓风"
                    else:
                        # 尝试提取第一个中文词
                        chinese_match = re.search(r'([\u4e00-\u9fff]+)', message)
                        if chinese_match:
                            up_name = chinese_match.group(1)
                
                # 智能分析完整流程
                has_search = "搜索" in message
                has_homepage = "主页" in message or "首页" in message
                has_play = "播放" in message and ("最新" in message or "一期" in message)
                
                # 如果是完整流程命令，生成多个步骤
                if has_search and has_homepage and has_play:
                    # 步骤1: 进入主页
                    steps.append({
                        "action": "bilibili_open_up",
                        "params": {"up_name": up_name},
                        "description": f"在B站搜索{up_name}并进入主页"
                    })
                    # 步骤2: 播放视频
                    steps.append({
                        "action": "bilibili_play_video",
                        "params": {"up_name": up_name},
                        "description": f"播放{up_name}的最新视频"
                    })
                else:
                    # 只进入主页
                    steps.append({
                        "action": "bilibili_open_up",
                        "params": {"up_name": up_name},
                        "description": f"在B站搜索{up_name}并进入主页"
                    })
            
            # 通用网站打开
            elif "打开" in message and ("网站" in message or "网页" in message):
                # 提取URL
                url_match = re.search(r'https?://[^\s]+', message)
                if url_match:
                    url = url_match.group()
                    steps.append({
                        "action": "open_website",
                        "params": {"url": url},
                        "description": f"打开网站: {url}"
                    })
            
            return steps
            
        except Exception as e:
            logger.error(f"智能命令识别失败: {e}")
            return []
    
    def split_commands_with_deepseek(self, message):
        """使用DeepSeek拆分命令"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            # 检查API密钥
            api_key = os.environ.get('DEEPSEEK_API_KEY')
            if not api_key:
                logger.warning("DEEPSEEK_API_KEY is required but not set")
                return []
            
            # 初始化DeepSeek
            llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=api_key,
                base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                temperature=0.1
            )
            
            # 构建提示词
            prompt = f"""
请将以下用户指令拆分为具体的可执行步骤。每个步骤应该是独立的、可执行的命令。

用户指令: {message}

请按照以下格式返回JSON数组，每个元素包含：
- "action": 操作类型 (如: "open_website", "desktop_scan", "web_search", "bilibili_open_up" 等)
- "params": 参数字典
- "description": 步骤描述

支持的操作类型：
- "open_website": 打开网站
- "bilibili_open_up": 打开UP主主页（使用浏览器上下文）
- "bilibili_play_video": 播放B站视频（复用已打开的浏览器实例）
- "click_element": 点击页面元素
- "automate_page": 页面自动化

重要说明：
- bilibili_open_up 和 bilibili_play_video 使用共享的浏览器上下文
- 后续操作会复用前序操作打开的浏览器实例
- 避免重复打开浏览器，提高效率

示例格式:
[
    {{
        "action": "bilibili_open_up",
        "params": {{"up_name": "影视飓风"}},
        "description": "在B站搜索影视飓风并进入主页"
    }},
    {{
        "action": "bilibili_play_video",
        "params": {{"up_name": "影视飓风"}},
        "description": "播放影视飓风的最新视频"
    }}
]

请只返回JSON数组，不要包含其他文字。
"""
            
            # 调用DeepSeek
            response = llm.invoke([HumanMessage(content=prompt)])
            result_text = response.content.strip()
            
            # 解析JSON
            import json
            try:
                # 尝试直接解析
                steps = json.loads(result_text)
            except:
                # 如果失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
                if json_match:
                    steps = json.loads(json_match.group())
                else:
                    steps = []
            
            return steps if isinstance(steps, list) else []
            
        except Exception as e:
            logger.error(f"DeepSeek命令拆分失败: {e}")
            return []
    
    def execute_single_command(self, step):
        """执行单个命令步骤"""
        try:
            action = step.get('action', '')
            params = step.get('params', {})
            
            # 根据action类型执行相应操作
            if action == 'bilibili_open_up':
                return self.execute_bilibili_open_up(params)
            elif action == 'bilibili_play_video':
                return self.execute_bilibili_play_video(params)
            elif action == 'open_website':
                return self.execute_open_website(params)
            elif action == 'desktop_scan':
                return self.execute_desktop_scan(params)
            elif action == 'web_search':
                return self.execute_web_search(params)
            elif action == 'play_video':
                return self.execute_play_video(params)
            elif action == 'click_element':
                return self.execute_click_element(params)
            elif action == 'automate_page':
                return self.execute_automate_page(params)
            elif action == 'run_command':
                return self.execute_run_command(params)
            else:
                return {
                    'success': False,
                    'error': f'不支持的操作类型: {action}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'执行命令失败: {str(e)}'
            }
    
    
    def execute_bilibili_open_up(self, params):
        """执行打开B站UP主主页"""
        try:
            from src.tools.executor import executor
            up_name = params.get('up_name', '')
            result = executor.execute_action("bilibili_open_up", {"up_name": up_name})
            return {
                'success': result.get('success', False),
                'message': f"打开UP主主页: {up_name}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'打开UP主主页失败: {str(e)}'
            }
    
    def execute_bilibili_play_video(self, params):
        """执行播放B站视频"""
        try:
            from src.tools.executor import executor
            up_name = params.get('up_name', '')
            result = executor.execute_action("bilibili_play_video", {"up_name": up_name})
            return {
                'success': result.get('success', False),
                'message': f"播放视频: {up_name}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'播放视频失败: {str(e)}'
            }
    
    
    def execute_open_website(self, params):
        """执行打开网站"""
        try:
            from src.tools.executor import executor
            url = params.get('url', '')
            result = executor.execute_action("open_website", {"url": url})
            return {
                'success': result.get('success', False),
                'message': f"打开网站: {url}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'打开网站失败: {str(e)}'
            }
    
    def execute_desktop_scan(self, params):
        """执行桌面扫描"""
        try:
            from src.tools.executor import executor
            result = executor.execute_action("run_command", {"command": "dir"})
            return {
                'success': result.get('success', False),
                'message': "桌面扫描完成",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'桌面扫描失败: {str(e)}'
            }
    
    def execute_web_search(self, params):
        """执行网络搜索"""
        try:
            from src.tools.executor import executor
            keyword = params.get('keyword', '')
            result = executor.execute_action("search_web", {"query": keyword})
            return {
                'success': result.get('success', False),
                'message': f"网络搜索: {keyword}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'网络搜索失败: {str(e)}'
            }
    
    def execute_play_video(self, params):
        """执行播放视频"""
        try:
            from src.tools.executor import executor
            video_url = params.get('url', '')
            result = executor.execute_action("play_video", {"url": video_url})
            return {
                'success': result.get('success', False),
                'message': f"播放视频: {video_url}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'播放视频失败: {str(e)}'
            }
    
    def execute_click_element(self, params):
        """执行点击元素"""
        try:
            from src.tools.executor import executor
            selector = params.get('selector', '')
            result = executor.execute_action("automate_page", {"query": f"点击元素: {selector}"})
            return {
                'success': result.get('success', False),
                'message': f"点击元素: {selector}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'点击元素失败: {str(e)}'
            }
    
    def execute_automate_page(self, params):
        """执行页面自动化"""
        try:
            from src.tools.executor import executor
            query = params.get('query', '')
            result = executor.execute_action("automate_page", {"query": query})
            return {
                'success': result.get('success', False),
                'message': f"页面自动化: {query}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'页面自动化失败: {str(e)}'
            }
    
    def execute_run_command(self, params):
        """执行系统命令"""
        try:
            from src.tools.executor import executor
            command = params.get('command', '')
            result = executor.execute_action("run_command", {"command": command})
            return {
                'success': result.get('success', False),
                'message': f"执行命令: {command}",
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行命令失败: {str(e)}'
            }
    
    def append_to_chat(self, sender, message, tag="info"):
        """添加消息到聊天区域"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_text.insert(tk.END, f"{sender}: ", "user" if sender == "用户" else "ai")
        self.chat_text.insert(tk.END, f"{message}\n", tag)
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def apply_styles(self):
        """统一的深色主题样式"""
        try:
            style = ttk.Style()
            # 使用可定制主题
            try:
                style.theme_use('clam')
            except Exception:
                pass

            accent = self.colors['accent']
            bg_main = self.colors['bg_main']
            bg_card = self.colors['bg_card']
            text_primary = self.colors['text_primary']

            style.configure('TFrame', background=bg_main)
            style.configure('Card.TFrame', background=bg_card)
            style.configure('TLabel', background=bg_main, foreground=text_primary, font=('Segoe UI', 11))
            style.configure('Card.TLabel', background=bg_card, foreground=text_primary, font=('Segoe UI', 11))

            style.configure('TButton', background=bg_card, foreground=text_primary, font=('Segoe UI', 11), borderwidth=0, focusthickness=0)
            style.map('TButton', background=[('active', self.colors['bg_hover'])])

            style.configure('Accent.TButton', background=accent, foreground=text_primary, font=('Segoe UI', 11, 'bold'))
            style.map('Accent.TButton', background=[('active', self.colors['accent_hover'])])

            # 进度条
            style.configure('Custom.Horizontal.TProgressbar', troughcolor=bg_card, bordercolor=bg_card,
                            background=accent, lightcolor=accent, darkcolor=accent)
        except Exception:
            pass
    
    def add_to_history(self, message):
        """添加到历史记录"""
        self.history_listbox.insert(tk.END, message)
        self.history_listbox.see(tk.END)
    
    def on_history_select(self, event):
        """历史记录选择事件"""
        selection = self.history_listbox.curselection()
        if selection:
            message = self.history_listbox.get(selection[0])
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, message)
            self.input_text.config(fg=self.colors['text_primary'])
    
    def on_input_change(self, event):
        """输入变化事件"""
        pass
    
    def on_input_focus_in(self, event):
        """输入框获得焦点"""
        if self.input_text.get(1.0, tk.END).strip() == "输入消息...":
            self.input_text.delete(1.0, tk.END)
            self.input_text.config(fg=self.colors['text_primary'])
    
    def on_input_focus_out(self, event):
        """输入框失去焦点"""
        if not self.input_text.get(1.0, tk.END).strip():
            self.input_text.insert(1.0, "输入消息...")
            self.input_text.config(fg=self.colors['text_muted'])
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def new_conversation(self):
        """新对话"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.conversation_history.clear()
        self.history_listbox.delete(0, tk.END)
        self.append_to_chat("系统", "开始新对话", "system")
    
    # 工具方法
    def scan_desktop(self):
        """扫描桌面"""
        self.append_to_chat("系统", "正在扫描桌面文件...", "info")
        self.update_status("扫描桌面中...")
        
        def scan():
            try:
                result = executor.execute_action("desktop_scan", {"file_type": "all"})
                self.root.after(0, lambda: self.append_to_chat("系统", f"扫描完成: {result}", "success"))
                self.root.after(0, lambda: self.update_status("扫描完成"))
            except Exception as e:
                self.root.after(0, lambda: self.append_to_chat("系统", f"扫描失败: {str(e)}", "error"))
                self.root.after(0, lambda: self.update_status("扫描失败"))
        
        threading.Thread(target=scan, daemon=True).start()
    
    def launch_file(self):
        """启动文件"""
        self.append_to_chat("系统", "请输入要启动的文件名", "info")
    
    def web_automation(self):
        """网页自动化"""
        self.append_to_chat("系统", "网页自动化功能开发中...", "info")
    
    def bilibili_operation(self):
        """B站操作"""
        self.append_to_chat("系统", "B站操作功能开发中...", "info")
    
    def steam_operation(self):
        """Steam操作"""
        self.append_to_chat("系统", "Steam操作功能开发中...", "info")
    
    def system_info(self):
        """系统信息"""
        self.append_to_chat("系统", "系统信息功能开发中...", "info")

    # ----- 淘宝动作（UI 触发） -----

    def taobao_search_action(self):
        try:
            from src.tools.executor import executor
            shop = "乔尔的桌搭小店"
            keyword = "金字塔"
            res = executor.execute_action("taobao_search_product", {"shop_name": shop, "product_keyword": keyword})
            ok = res.get('result', {}).get('success') if isinstance(res, dict) else False
            self.append_to_chat("系统", res.get('result', {}).get('message', '已尝试淘宝搜索'), "success" if ok else "warning")
        except Exception as e:
            self.append_to_chat("系统", f"淘宝搜索失败: {e}", "error")

    def taobao_buy_action(self):
        try:
            from src.tools.executor import executor
            res = executor.execute_action("taobao_buy", {})
            ok = res.get('result', {}).get('success') if isinstance(res, dict) else False
            self.append_to_chat("系统", res.get('result', {}).get('message', '已尝试淘宝下单/加购'), "success" if ok else "warning")
        except Exception as e:
            self.append_to_chat("系统", f"淘宝购买失败: {e}", "error")

    def taobao_quick_buy_action(self):
        """按顺序触发两步，确保上下文串联"""
        try:
            # 直接执行搜索和购买，登录由自动登录功能处理
            self.taobao_search_action()
            self.root.after(2000, lambda: self.taobao_buy_action())
        except Exception as e:
            self.append_to_chat("系统", f"淘宝一键下单失败: {e}", "error")
    
    # 凭据管理方法
    def refresh_credential_list(self):
        """刷新凭据列表"""
        try:
            # 清空列表
            for item in self.credential_tree.get_children():
                self.credential_tree.delete(item)
            
            # 加载凭据数据
            result = credential_db.get_all_credentials()
            if result["success"]:
                for cred in result["credentials"]:
                    self.credential_tree.insert('', 'end', values=(
                        cred["application"],
                        cred["account"],
                        cred["username"]
                    ), tags=(cred["id"],))
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新凭据列表失败: {str(e)}")
            logger.error(f"刷新凭据列表失败: {e}")
    
    def on_credential_search(self, event):
        """凭据搜索事件处理"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_credential_list()
            return
        
        try:
            # 清空列表
            for item in self.credential_tree.get_children():
                self.credential_tree.delete(item)
            
            # 执行搜索
            result = credential_db.search_credentials(keyword)
            if result["success"]:
                for cred in result["credentials"]:
                    self.credential_tree.insert('', 'end', values=(
                        cred["application"],
                        cred["account"],
                        cred["username"]
                    ), tags=(cred["id"],))
            else:
                messagebox.showwarning("警告", result["error"])
                
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")
            logger.error(f"搜索失败: {e}")
    
    def on_credential_select(self, event):
        """凭据选择事件处理"""
        selection = self.credential_tree.selection()
        if selection:
            item = self.credential_tree.item(selection[0])
            credential_id = int(item['tags'][0])
            self.load_credential_details(credential_id)
    
    def load_credential_details(self, credential_id):
        """加载凭据详情"""
        try:
            result = credential_db.get_credential(credential_id)
            if result["success"]:
                cred = result["credential"]
                self.current_credential_id = credential_id
                
                # 填充表单
                self.form_vars['account'].set(cred["account"])
                self.form_vars['password'].set(cred["password"])
                self.form_vars['application'].set(cred["application"])
                self.form_vars['contact'].set(cred.get("contact", ""))
                self.form_vars['website_url'].set(cred.get("website_url", ""))
                
                # 处理备注字段
                if 'notes' in self.form_entries and isinstance(self.form_entries['notes'], tk.Text):
                    self.form_entries['notes'].delete(1.0, tk.END)
                    self.form_entries['notes'].insert(1.0, cred.get("notes", ""))
                else:
                    self.form_vars['notes'].set(cred.get("notes", ""))
                    
        except Exception as e:
            messagebox.showerror("错误", f"加载凭据详情失败: {str(e)}")
            logger.error(f"加载凭据详情失败: {e}")
    
    def add_credential(self):
        """添加凭据"""
        self.clear_credential_form()
        self.current_credential_id = None
    
    def edit_credential(self):
        """编辑凭据"""
        if not self.current_credential_id:
            messagebox.showwarning("警告", "请先选择要编辑的凭据")
            return

    def save_credential(self):
        """保存凭据（新增或更新）"""
        try:
            from src.database.credential_db import credential_db
            # 读取表单
            def get_text(field):
                if field == 'notes' and isinstance(self.form_entries.get(field), tk.Text):
                    return self.form_entries[field].get(1.0, tk.END).strip()
                return self.form_vars.get(field).get().strip() if field in self.form_vars else ''

            account = get_text('account')
            password = get_text('password')
            application = get_text('application')
            contact = get_text('contact')
            website_url = get_text('website_url')
            notes = get_text('notes')

            if not account or not password or not application:
                messagebox.showwarning("提示", "请至少填写 账号、密码、应用 三项")
                return

            # DB 要求 username 不为空，这里用 account 作为 username 保存
            if self.current_credential_id is None:
                res = credential_db.add_credential(
                    username=account,
                    account=account,
                    password=password,
                    application=application,
                    contact=contact,
                    website_url=website_url,
                    notes=notes,
                )
                if res.get('success'):
                    self.append_to_chat("系统", "凭据已新增", "success")
                    self.refresh_credential_list()
                    self.current_credential_id = res.get('credential_id')
                else:
                    messagebox.showerror("错误", res.get('error', '新增失败'))
            else:
                update_kwargs = {
                    'account': account,
                    'password': password,
                    'application': application,
                    'contact': contact,
                    'website_url': website_url,
                    'notes': notes,
                }
                res = credential_db.update_credential(self.current_credential_id, **update_kwargs)
                if res.get('success'):
                    self.append_to_chat("系统", "凭据已保存", "success")
                    self.refresh_credential_list()
                else:
                    messagebox.showerror("错误", res.get('error', '保存失败'))
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def delete_credential(self):
        """删除凭据"""
        if not self.current_credential_id:
            messagebox.showwarning("警告", "请先选择要删除的凭据")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的凭据吗？"):
            try:
                result = credential_db.delete_credential(self.current_credential_id)
                if result["success"]:
                    messagebox.showinfo("成功", "凭据删除成功")
                    self.clear_credential_form()
                    self.refresh_credential_list()
                else:
                    messagebox.showerror("错误", result["error"])
            except Exception as e:
                messagebox.showerror("错误", f"删除凭据失败: {str(e)}")
                logger.error(f"删除凭据失败: {e}")
    
    def clear_credential_form(self):
        """清空凭据表单"""
        for field, var in self.form_vars.items():
            if field == 'notes' and isinstance(self.form_entries.get(field), tk.Text):
                self.form_entries[field].delete(1.0, tk.END)
            else:
                var.set("")
        self.current_credential_id = None

    # --- 凭据快捷操作 ---
    def copy_field_to_clipboard(self, field: str):
        try:
            value = None
            if field == 'notes' and isinstance(self.form_entries.get(field), tk.Text):
                value = self.form_entries[field].get(1.0, tk.END).strip()
            else:
                value = self.form_vars.get(field).get().strip() if field in self.form_vars else ''
            if value:
                self.root.clipboard_clear()
                self.root.clipboard_append(value)
                self.append_to_chat("系统", f"已复制 {field} 到剪贴板", "success")
            else:
                self.append_to_chat("系统", f"{field} 为空，未复制", "warning")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")

    def open_credential_website(self):
        try:
            url = self.form_vars.get('website_url').get().strip()
            if not url:
                self.append_to_chat("系统", "网站URL为空", "warning")
                return
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'https://' + url
            webbrowser.open(url)
            self.append_to_chat("系统", f"已打开网站: {url}", "success")
        except Exception as e:
            messagebox.showerror("错误", f"打开网站失败: {e}")
    
    # 命令处理方法
    def handle_desktop_scan(self):
        """处理桌面扫描"""
        self.scan_desktop()
    
    def handle_desktop_launch(self, message):
        """处理桌面启动"""
        self.append_to_chat("系统", f"桌面启动: {message}", "info")
    
    def handle_web_automation(self, message):
        """处理网页自动化"""
        self.append_to_chat("系统", f"网页自动化: {message}", "info")
    
    def handle_bilibili(self, message):
        """处理B站操作"""
        self.append_to_chat("系统", f"B站操作: {message}", "info")


def main():
    """主函数"""
    root = tk.Tk()
    app = ChatGPTUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
