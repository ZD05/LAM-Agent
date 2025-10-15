#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAM-Agent 统一UI应用程序
结合主界面和凭据管理器
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
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

class UnifiedLAMApp:
    """统一LAM-Agent应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.agent: Optional[LamAgent] = None
        self.conversation_history = []
        self.command_recognizer = CommandRecognizer()
        self.current_view = "main"  # "main" 或 "credentials"
        
        # ChatGPT风格配色方案
        self.colors = {
            'bg_main': '#202123',      # 主背景色
            'bg_sidebar': '#171717',    # 侧边栏背景色
            'bg_input': '#2C2D30',     # 输入框背景色
            'bg_card': '#2F2F2F',      # 卡片背景色
            'text_primary': '#FFFFFF',  # 主要文字颜色
            'text_secondary': '#C5C5D2', # 次要文字颜色
            'text_muted': '#8E8EA0',   # 静音文字颜色
            'accent': '#10A37F',       # 强调色
            'accent_hover': '#0D8F6B',  # 强调色悬停
            'border': '#3C3C3C',       # 边框颜色
            'hover': '#40414F',        # 悬停背景色
            'success': '#10A37F',      # 成功色
            'warning': '#FFA500',      # 警告色
            'error': '#FF6B6B'         # 错误色
        }
        
        self.setup_ui()
        self.setup_agent()
        
    def setup_ui(self):
        """设置统一用户界面"""
        self.root.title("LAM-Agent Pro - 智能助手")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors['bg_main'])
        
        # 创建顶部导航栏
        self.create_top_navigation()
        
        # 创建主容器
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 创建主界面
        self.create_main_interface()
        
        # 创建凭据管理器界面
        self.create_credential_interface()
        
        # 默认显示主界面
        self.show_main_interface()
        
    def create_top_navigation(self):
        """创建顶部导航栏"""
        nav_frame = tk.Frame(self.root, bg=self.colors['bg_sidebar'], height=60)
        nav_frame.pack(fill=tk.X, padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # Logo和标题
        logo_frame = tk.Frame(nav_frame, bg=self.colors['bg_sidebar'])
        logo_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        logo_label = tk.Label(logo_frame, text="🤖", font=('Arial', 20), 
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(logo_frame, text="LAM-Agent Pro", font=('Arial', 16, 'bold'),
                              bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 导航按钮
        nav_buttons_frame = tk.Frame(nav_frame, bg=self.colors['bg_sidebar'])
        nav_buttons_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 主界面按钮
        self.main_btn = tk.Button(nav_buttons_frame, text="🏠 主界面", 
                                 command=self.show_main_interface,
                                 bg=self.colors['accent'], fg=self.colors['text_primary'],
                                 font=('Arial', 12), relief=tk.FLAT, bd=0,
                                 activebackground=self.colors['accent_hover'],
                                 cursor='hand2', padx=20, pady=8)
        self.main_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 凭据管理器按钮
        self.credential_btn = tk.Button(nav_buttons_frame, text="🔐 凭据管理", 
                                       command=self.show_credential_interface,
                                       bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                                       font=('Arial', 12), relief=tk.FLAT, bd=0,
                                       activebackground=self.colors['hover'],
                                       cursor='hand2', padx=20, pady=8)
        self.credential_btn.pack(side=tk.LEFT)
        
    def create_main_interface(self):
        """创建主界面"""
        self.main_frame = tk.Frame(self.main_container, bg=self.colors['bg_main'])
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 配置网格权重
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # 创建侧边栏
        self.create_sidebar(content_frame)
        
        # 创建主聊天区域
        self.create_chat_area(content_frame)
        
        # 创建底部输入区域
        self.create_input_area(content_frame)
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_credential_interface(self):
        """创建凭据管理器界面"""
        self.credential_frame = tk.Frame(self.main_container, bg=self.colors['bg_main'])
        
        # 顶部操作栏
        self.create_credential_top_bar()
        
        # 主内容区域
        self.create_credential_content()
        
    def create_credential_top_bar(self):
        """创建凭据管理器顶部操作栏"""
        top_bar = tk.Frame(self.credential_frame, bg=self.colors['bg_main'], height=60)
        top_bar.pack(fill=tk.X, padx=20, pady=20)
        top_bar.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(top_bar, text="🔐 凭据管理器", font=('Arial', 18, 'bold'),
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = tk.Frame(top_bar, bg=self.colors['bg_main'])
        button_frame.pack(side=tk.RIGHT)
        
        # 添加按钮
        add_btn = tk.Button(button_frame, text="➕ 添加", command=self.add_credential,
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           font=('Arial', 12), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['accent_hover'],
                           cursor='hand2', padx=20, pady=8)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 修改按钮
        edit_btn = tk.Button(button_frame, text="✏️ 修改", command=self.edit_credential,
                            bg=self.colors['warning'], fg=self.colors['text_primary'],
                            font=('Arial', 12), relief=tk.FLAT, bd=0,
                            activebackground='#E6940A',
                            cursor='hand2', padx=20, pady=8)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 删除按钮
        delete_btn = tk.Button(button_frame, text="🗑️ 删除", command=self.delete_credential,
                              bg=self.colors['error'], fg=self.colors['text_primary'],
                              font=('Arial', 12), relief=tk.FLAT, bd=0,
                              activebackground='#E55A5A',
                              cursor='hand2', padx=20, pady=8)
        delete_btn.pack(side=tk.LEFT)
        
    def create_credential_content(self):
        """创建凭据管理器内容区域"""
        # 主内容框架
        content_frame = tk.Frame(self.credential_frame, bg=self.colors['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 左侧凭据列表
        self.create_credential_list(content_frame)
        
        # 右侧凭据详情
        self.create_credential_details(content_frame)
        
    def create_credential_list(self, parent):
        """创建凭据列表"""
        # 左侧框架
        left_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 搜索区域
        search_frame = tk.Frame(left_frame, bg=self.colors['bg_card'])
        search_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 搜索框
        search_label = tk.Label(search_frame, text="🔍 搜索凭据:", font=('Arial', 12, 'bold'),
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
        list_title = tk.Label(list_frame, text="📋 凭据列表", font=('Arial', 12, 'bold'),
                             bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        list_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 创建Treeview
        columns = ('应用', '账号', '用户名')
        self.credential_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # 设置列标题和宽度
        column_widths = {'应用': 80, '账号': 120, '用户名': 60}
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
        detail_title = tk.Label(right_frame, text="📝 凭据详情", font=('Arial', 16, 'bold'),
                               bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        detail_title.pack(anchor=tk.W, padx=20, pady=20)
        
        # 表单容器
        form_container = tk.Frame(right_frame, bg=self.colors['bg_card'])
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 表单字段
        fields = [
            ('用户名', 'username'),
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
            label_widget = tk.Label(field_frame, text=f"{label}:", font=('Arial', 12, 'bold'),
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
        
        # 密码显示/隐藏按钮
        password_frame = tk.Frame(form_container, bg=self.colors['bg_card'])
        password_frame.pack(fill=tk.X, pady=10)
        
        self.show_password_var = tk.BooleanVar()
        show_password_cb = tk.Checkbutton(password_frame, text="显示密码", variable=self.show_password_var, 
                                         command=self.toggle_password_visibility,
                                         bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                                         font=('Arial', 10), selectcolor=self.colors['bg_input'],
                                         activebackground=self.colors['bg_card'],
                                         activeforeground=self.colors['text_secondary'])
        show_password_cb.pack(anchor=tk.W)
        
        # 当前选中的凭据ID
        self.current_credential_id = None
        
    def show_main_interface(self):
        """显示主界面"""
        self.current_view = "main"
        self.credential_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 更新按钮状态
        self.main_btn.config(bg=self.colors['accent'])
        self.credential_btn.config(bg=self.colors['bg_input'])
        
    def show_credential_interface(self):
        """显示凭据管理器界面"""
        self.current_view = "credentials"
        self.main_frame.pack_forget()
        self.credential_frame.pack(fill=tk.BOTH, expand=True)
        
        # 更新按钮状态
        self.main_btn.config(bg=self.colors['bg_input'])
        self.credential_btn.config(bg=self.colors['accent'])
        
        # 刷新凭据列表
        self.refresh_credential_list()
        
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
                self.form_vars['username'].set(cred["username"])
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
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        if hasattr(self, 'form_entries') and 'password' in self.form_entries:
            if self.show_password_var.get():
                self.form_entries['password'].config(show='')
            else:
                self.form_entries['password'].config(show='*')
    
    def save_credential(self):
        """保存凭据"""
        try:
            # 获取表单数据
            username = self.form_vars['username'].get().strip()
            account = self.form_vars['account'].get().strip()
            password = self.form_vars['password'].get().strip()
            application = self.form_vars['application'].get().strip()
            contact = self.form_vars['contact'].get().strip()
            website_url = self.form_vars['website_url'].get().strip()
            
            # 处理备注字段
            if 'notes' in self.form_entries and isinstance(self.form_entries['notes'], tk.Text):
                notes = self.form_entries['notes'].get(1.0, tk.END).strip()
            else:
                notes = self.form_vars['notes'].get().strip()
            
            # 验证必填字段
            if not all([username, account, password, application]):
                messagebox.showwarning("警告", "请填写所有必填字段")
                return
            
            if self.current_credential_id:
                # 更新凭据
                result = credential_db.update_credential(
                    self.current_credential_id, username, account, password, 
                    application, contact, website_url, notes
                )
                if result["success"]:
                    messagebox.showinfo("成功", "凭据更新成功")
                    self.refresh_credential_list()
                else:
                    messagebox.showerror("错误", result["error"])
            else:
                # 添加新凭据
                result = credential_db.add_credential(
                    username, account, password, application, contact, website_url, notes
                )
                if result["success"]:
                    messagebox.showinfo("成功", "凭据添加成功")
                    self.clear_credential_form()
                    self.refresh_credential_list()
                else:
                    messagebox.showerror("错误", result["error"])
                    
        except Exception as e:
            messagebox.showerror("错误", f"保存凭据失败: {str(e)}")
            logger.error(f"保存凭据失败: {e}")
    
    # 以下是主界面的方法，从原来的main_window.py移植过来
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="清空对话", command=self.clear_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="桌面扫描", command=self._quick_scan_desktop)
        tools_menu.add_command(label="配置设置", command=self.open_config_dialog)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_sidebar(self, parent):
        """创建侧边栏"""
        sidebar = tk.Frame(parent, bg=self.colors['bg_sidebar'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # 顶部区域
        top_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        top_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 功能标题
        func_title = tk.Label(top_frame, text="🛠️ 功能面板", font=('Arial', 14, 'bold'),
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        func_title.pack(anchor=tk.W, pady=(0, 20))
        
        # 桌面操作按钮
        desktop_frame = tk.Frame(top_frame, bg=self.colors['bg_sidebar'])
        desktop_frame.pack(fill=tk.X, pady=(0, 20))
        
        desktop_title = tk.Label(desktop_frame, text="📁 桌面操作", font=('Arial', 12, 'bold'),
                                bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        desktop_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 桌面操作按钮
        desktop_buttons = [
            ("🔍 扫描桌面", self._quick_scan_desktop),
            ("🔎 搜索文件", self._quick_search_files),
            ("🚀 启动文件", self._quick_launch_file),
            ("📊 桌面管理", self.open_desktop_dialog)
        ]
        
        for text, command in desktop_buttons:
            btn = tk.Button(desktop_frame, text=text, command=command,
                           bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'],
                           font=('Arial', 11), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['hover'],
                           activeforeground=self.colors['text_primary'],
                           cursor='hand2', anchor=tk.W)
            btn.pack(fill=tk.X, pady=2)
        
        # 对话历史
        history_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        history_title = tk.Label(history_frame, text="💬 对话历史", font=('Arial', 12, 'bold'),
                                bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        history_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 历史列表
        self.history_listbox = tk.Listbox(history_frame, bg=self.colors['bg_input'], 
                                         fg=self.colors['text_primary'], font=('Arial', 10),
                                         selectbackground=self.colors['hover'],
                                         relief=tk.FLAT, bd=0)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 绑定历史选择事件
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)
    
    def create_chat_area(self, parent):
        """创建聊天区域"""
        chat_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 聊天标题
        chat_title = tk.Label(chat_frame, text="💬 对话区域", font=('Arial', 14, 'bold'),
                             bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        chat_title.pack(anchor=tk.W, padx=20, pady=20)
        
        # 聊天文本区域
        text_frame = tk.Frame(chat_frame, bg=self.colors['bg_card'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.chat_text = scrolledtext.ScrolledText(
            text_frame, 
            font=("Consolas", 11),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.colors['bg_input'],
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=0,
            insertbackground=self.colors['text_primary']
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置文本标签样式
        self.chat_text.tag_configure("user", foreground="#4A9EFF", font=("Arial", 11, "bold"))
        self.chat_text.tag_configure("ai", foreground="#10A37F", font=("Arial", 11))
        self.chat_text.tag_configure("system", foreground="#8E8EA0", font=("Arial", 10, "italic"))
        self.chat_text.tag_configure("error", foreground="#FF6B6B", font=("Arial", 11, "bold"))
        self.chat_text.tag_configure("info", foreground="#8E8EA0", font=("Arial", 10))
        self.chat_text.tag_configure("success", foreground="#10A37F", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("warning", foreground="#FFA500", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("timestamp", foreground="#8E8EA0", font=("Arial", 9))
        self.chat_text.tag_configure("separator", foreground="#3C3C3C")
    
    def create_input_area(self, parent):
        """创建输入区域"""
        input_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        input_frame.pack(side=tk.LEFT, fill=tk.X, pady=(0, 10))
        
        # 输入标题
        input_title = tk.Label(input_frame, text="⌨️ 输入区域", font=('Arial', 14, 'bold'),
                              bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        input_title.pack(anchor=tk.W, padx=20, pady=20)
        
        # 输入容器
        input_container = tk.Frame(input_frame, bg=self.colors['bg_card'])
        input_container.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 输入文本框
        self.input_text = tk.Text(input_container, height=4, wrap=tk.WORD, 
                                 font=("Arial", 11), bg=self.colors['bg_input'],
                                 fg=self.colors['text_primary'], relief=tk.FLAT, bd=0,
                                 insertbackground=self.colors['text_primary'])
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 发送按钮
        send_btn = tk.Button(input_container, text="📤 发送", command=self.send_message,
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           font=('Arial', 12), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['accent_hover'],
                           cursor='hand2', padx=20, pady=10)
        send_btn.pack(side=tk.RIGHT)
        
        # 命令建议框架
        self.suggestion_frame = tk.Frame(input_frame, bg=self.colors['bg_card'])
        self.suggestion_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 命令建议标签
        self.suggestion_label = tk.Label(self.suggestion_frame, text="💡 命令建议:", 
                                       font=("Arial", 10, "italic"), 
                                       bg=self.colors['bg_card'], fg=self.colors['text_secondary'])
        self.suggestion_label.pack(anchor=tk.W)
        
        # 命令建议按钮框架
        self.suggestion_buttons_frame = tk.Frame(self.suggestion_frame, bg=self.colors['bg_card'])
        self.suggestion_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 绑定回车键发送
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
        
        # 绑定输入事件
        self.input_text.bind('<KeyRelease>', self.on_input_change)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Frame(self.main_frame, bg=self.colors['bg_sidebar'], height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        # 状态标签
        self.status_label = tk.Label(self.status_bar, text="就绪", 
                                    bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                                    font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # 时间标签
        self.time_label = tk.Label(self.status_bar, text="", 
                                  bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                                  font=('Arial', 10))
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # 更新时间
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def setup_agent(self):
        """设置智能代理"""
        try:
            self.agent = LamAgent()
            self.append_to_chat("系统", "LAM-Agent 已启动，可以开始对话！", "system")
            self.update_status("智能代理已启动")
        except Exception as e:
            self.append_to_chat("系统", f"启动智能代理失败: {str(e)}", "error")
            self.update_status("智能代理启动失败")
            logger.error(f"启动智能代理失败: {e}")
    
    def send_message(self):
        """发送消息"""
        message = self.input_text.get(1.0, tk.END).strip()
        if not message:
            return
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        
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
            # 识别命令类型
            command_type = self.command_recognizer.recognize_command(message)
            
            if command_type == CommandType.DESKTOP_SCAN:
                self.handle_desktop_scan()
            elif command_type == CommandType.DESKTOP_LAUNCH:
                self.handle_desktop_launch(message)
            elif command_type == CommandType.WEB_AUTOMATION:
                self.handle_web_automation(message)
            elif command_type == CommandType.BILIBILI:
                self.handle_bilibili(message)
            else:
                # 使用智能代理处理
                if self.agent:
                    response = self.agent.process_message(message)
                    self.root.after(0, lambda: self.append_to_chat("AI", response, "ai"))
                    self.root.after(0, lambda: self.update_status("就绪"))
                else:
                    self.root.after(0, lambda: self.append_to_chat("系统", "智能代理未启动", "error"))
                    self.root.after(0, lambda: self.update_status("智能代理未启动"))
                    
        except Exception as e:
            error_msg = f"处理消息失败: {str(e)}"
            self.root.after(0, lambda: self.append_to_chat("系统", error_msg, "error"))
            self.root.after(0, lambda: self.update_status("处理失败"))
            logger.error(f"处理消息失败: {e}")
    
    def append_to_chat(self, sender, message, tag="info"):
        """添加消息到聊天区域"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_text.insert(tk.END, f"{sender}: ", "user" if sender == "用户" else "ai")
        self.chat_text.insert(tk.END, f"{message}\n", tag)
        self.chat_text.insert(tk.END, "-" * 50 + "\n", "separator")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
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
    
    def on_input_change(self, event):
        """输入变化事件"""
        # 这里可以添加实时建议功能
        pass
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
    
    def clear_conversation(self):
        """清空对话"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.conversation_history.clear()
        self.history_listbox.delete(0, tk.END)
    
    def _quick_scan_desktop(self):
        """快速扫描桌面"""
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
    
    def _quick_search_files(self):
        """快速搜索文件"""
        self.append_to_chat("系统", "请输入要搜索的文件名", "info")
    
    def _quick_launch_file(self):
        """快速启动文件"""
        self.append_to_chat("系统", "请输入要启动的文件名", "info")
    
    def open_desktop_dialog(self):
        """打开桌面管理对话框"""
        self.append_to_chat("系统", "桌面管理功能开发中...", "info")
    
    def open_config_dialog(self):
        """打开配置对话框"""
        self.append_to_chat("系统", "配置功能开发中...", "info")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
LAM-Agent Pro v1.0
智能桌面助手

功能特性:
• 智能对话交互
• 桌面文件管理
• 网页自动化
• B站视频操作
• 凭据管理

技术栈:
• Python + Tkinter
• DeepSeek AI
• MCP协议
        """
        messagebox.showinfo("关于 LAM-Agent Pro", about_text)
    
    def handle_desktop_scan(self):
        """处理桌面扫描"""
        self._quick_scan_desktop()
    
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
    app = UnifiedLAMApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


