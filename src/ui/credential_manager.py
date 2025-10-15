#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import logging
from typing import Dict, Any, List, Optional
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database.credential_db import credential_db

logger = logging.getLogger(__name__)

class CredentialManagerUI:
    """凭据管理器UI界面 - ChatGPT风格"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LAM-Agent 凭据管理器")
        self.root.geometry("1400x900")
        
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
        
        # 配置根窗口
        self.root.configure(bg=self.colors['bg_main'])
        
        # 当前选中的凭据ID
        self.current_credential_id = None
        
        # 创建UI组件
        self.create_widgets()
        
        # 加载数据
        self.refresh_data()
    
    def create_widgets(self):
        """创建UI组件"""
        # 配置网格权重
        self.root.columnconfigure(0, weight=0)  # 侧边栏固定宽度
        self.root.columnconfigure(1, weight=1)  # 主内容区域
        self.root.rowconfigure(0, weight=1)
        
        # 创建侧边栏
        self.create_sidebar()
        
        # 创建主内容区域
        self.create_main_content()
        
        # 配置样式
        self.configure_styles()
    
    def create_sidebar(self):
        """创建侧边栏"""
        # 侧边栏框架
        self.sidebar = tk.Frame(self.root, bg=self.colors['bg_sidebar'], width=280)
        self.sidebar.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # 顶部区域
        top_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        top_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Logo和标题
        logo_frame = tk.Frame(top_frame, bg=self.colors['bg_sidebar'])
        logo_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Logo图标 (使用文字代替)
        logo_label = tk.Label(logo_frame, text="🔐", font=('Arial', 24), 
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(logo_frame, text="凭据管理器", font=('Arial', 16, 'bold'),
                              bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 导航按钮
        self.create_navigation_buttons(top_frame)
        
        # 搜索区域
        self.create_search_section()
        
        # 凭据列表区域
        self.create_credential_list_section()
    
    def create_navigation_buttons(self, parent):
        """创建导航按钮"""
        nav_frame = tk.Frame(parent, bg=self.colors['bg_sidebar'])
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 新凭据按钮
        self.new_btn = self.create_nav_button(nav_frame, "➕ 新凭据", self.add_credential)
        self.new_btn.pack(fill=tk.X, pady=(0, 8))
        
        # 导入按钮
        self.import_btn = self.create_nav_button(nav_frame, "📥 导入", self.import_credentials)
        self.import_btn.pack(fill=tk.X, pady=(0, 8))
        
        # 导出按钮
        self.export_btn = self.create_nav_button(nav_frame, "📤 导出", self.export_credentials)
        self.export_btn.pack(fill=tk.X, pady=(0, 8))
        
        # 统计按钮
        self.stats_btn = self.create_nav_button(nav_frame, "📊 统计", self.show_statistics)
        self.stats_btn.pack(fill=tk.X, pady=(0, 8))
    
    def create_nav_button(self, parent, text, command):
        """创建导航按钮"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'],
                       font=('Arial', 12), relief=tk.FLAT, bd=0,
                       activebackground=self.colors['hover'],
                       activeforeground=self.colors['text_primary'],
                       cursor='hand2')
        
        # 绑定悬停效果
        def on_enter(e):
            btn.config(bg=self.colors['hover'])
        def on_leave(e):
            btn.config(bg=self.colors['bg_sidebar'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_search_section(self):
        """创建搜索区域"""
        search_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 搜索标题
        search_title = tk.Label(search_frame, text="搜索凭据", font=('Arial', 12, 'bold'),
                               bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        search_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 搜索框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                                    font=('Arial', 11), relief=tk.FLAT, bd=0,
                                    insertbackground=self.colors['text_primary'])
        self.search_entry.pack(fill=tk.X, pady=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # 分类筛选
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, 
                                          state="readonly", font=('Arial', 11))
        self.category_combo.pack(fill=tk.X, pady=(0, 10))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # 刷新按钮
        refresh_btn = tk.Button(search_frame, text="🔄 刷新", command=self.refresh_data,
                               bg=self.colors['accent'], fg=self.colors['text_primary'],
                               font=('Arial', 10), relief=tk.FLAT, bd=0,
                               activebackground=self.colors['accent_hover'],
                               cursor='hand2')
        refresh_btn.pack(fill=tk.X)
    
    def create_credential_list_section(self):
        """创建凭据列表区域"""
        list_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 列表标题
        list_title = tk.Label(list_frame, text="凭据列表", font=('Arial', 12, 'bold'),
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_primary'])
        list_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 创建凭据列表
        self.create_credential_list(list_frame)
    
    def create_credential_list(self, parent):
        """创建凭据列表"""
        # 创建Treeview
        columns = ('应用', '账号', '用户名')
        self.credential_tree = ttk.Treeview(parent, columns=columns, show='tree headings', height=15)
        
        # 设置列标题和宽度
        column_widths = {'应用': 80, '账号': 120, '用户名': 60}
        for col in columns:
            self.credential_tree.heading(col, text=col)
            self.credential_tree.column(col, width=column_widths[col])
        
        # 滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.credential_tree.yview)
        self.credential_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.credential_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.credential_tree.bind('<<TreeviewSelect>>', self.on_credential_select)
        
        # 右键菜单
        self.create_context_menu()
    
    def create_main_content(self):
        """创建主内容区域"""
        # 主内容框架
        self.main_content = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.main_content.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=0, pady=0)
        
        # 顶部栏
        self.create_top_bar()
        
        # 内容区域
        self.create_content_area()
    
    def create_top_bar(self):
        """创建顶部栏"""
        top_bar = tk.Frame(self.main_content, bg=self.colors['bg_main'], height=60)
        top_bar.pack(fill=tk.X, padx=20, pady=20)
        top_bar.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(top_bar, text="凭据详情", font=('Arial', 18, 'bold'),
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        # 右侧按钮
        button_frame = tk.Frame(top_bar, bg=self.colors['bg_main'])
        button_frame.pack(side=tk.RIGHT)
        
        # 保存按钮
        save_btn = tk.Button(button_frame, text="💾 保存", command=self.save_credential,
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           font=('Arial', 12), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['accent_hover'],
                           cursor='hand2', padx=20, pady=8)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 删除按钮
        delete_btn = tk.Button(button_frame, text="🗑️ 删除", command=self.delete_credential,
                              bg=self.colors['error'], fg=self.colors['text_primary'],
                              font=('Arial', 12), relief=tk.FLAT, bd=0,
                              activebackground='#E55A5A',
                              cursor='hand2', padx=20, pady=8)
        delete_btn.pack(side=tk.LEFT)
    
    def create_content_area(self):
        """创建内容区域"""
        # 内容框架
        content_frame = tk.Frame(self.main_content, bg=self.colors['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 创建凭据表单
        self.create_credential_form(content_frame)
    
    def create_credential_form(self, parent):
        """创建凭据表单"""
        # 表单容器
        form_container = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        form_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 表单内容
        form_content = tk.Frame(form_container, bg=self.colors['bg_card'])
        form_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
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
            field_frame = tk.Frame(form_content, bg=self.colors['bg_card'])
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
        password_frame = tk.Frame(form_content, bg=self.colors['bg_card'])
        password_frame.pack(fill=tk.X, pady=10)
        
        self.show_password_var = tk.BooleanVar()
        show_password_cb = tk.Checkbutton(password_frame, text="显示密码", variable=self.show_password_var, 
                                         command=self.toggle_password_visibility,
                                         bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                                         font=('Arial', 10), selectcolor=self.colors['bg_input'],
                                         activebackground=self.colors['bg_card'],
                                         activeforeground=self.colors['text_secondary'])
        show_password_cb.pack(anchor=tk.W)
    
    def configure_styles(self):
        """配置样式"""
        # 配置ttk样式
        style = ttk.Style()
        
        # 配置Treeview样式
        style.configure("Treeview", background=self.colors['bg_input'], 
                       foreground=self.colors['text_primary'], fieldbackground=self.colors['bg_input'],
                       borderwidth=0, font=('Arial', 10))
        
        style.configure("Treeview.Heading", background=self.colors['bg_sidebar'], 
                       foreground=self.colors['text_primary'], font=('Arial', 10, 'bold'))
        
        # 配置Combobox样式
        style.configure("TCombobox", background=self.colors['bg_input'], 
                       foreground=self.colors['text_primary'], fieldbackground=self.colors['bg_input'],
                       borderwidth=0, font=('Arial', 11))
        
        # 配置Scrollbar样式
        style.configure("Vertical.TScrollbar", background=self.colors['bg_sidebar'],
                       troughcolor=self.colors['bg_input'], borderwidth=0,
                       arrowcolor=self.colors['text_secondary'])
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self.edit_credential)
        self.context_menu.add_command(label="删除", command=self.delete_credential)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制账号", command=self.copy_account)
        self.context_menu.add_command(label="复制密码", command=self.copy_password)
        
        # 绑定右键事件
        self.credential_tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.credential_tree.selection()[0] if self.credential_tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    
    def refresh_data(self):
        """刷新数据"""
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
            
            # 加载分类数据
            categories_result = credential_db.get_application_categories()
            if categories_result["success"]:
                category_names = ["全部"] + [cat["category_name"] for cat in categories_result["categories"]]
                self.category_combo['values'] = category_names
                self.category_var.set("全部")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新数据失败: {str(e)}")
            logger.error(f"刷新数据失败: {e}")
    
    def on_search(self, event):
        """搜索事件处理"""
        # 延迟搜索，避免频繁查询
        self.root.after(500, self.search_credentials)
    
    def search_credentials(self):
        """搜索凭据"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_data()
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
    
    def on_category_change(self, event):
        """分类改变事件处理"""
        category = self.category_var.get()
        if category == "全部":
            self.refresh_data()
        else:
            try:
                # 清空列表
                for item in self.credential_tree.get_children():
                    self.credential_tree.delete(item)
                
                # 按分类加载
                result = credential_db.get_all_credentials(category)
                if result["success"]:
                    for cred in result["credentials"]:
                        self.credential_tree.insert('', 'end', values=(
                            cred["application"],
                            cred["account"],
                            cred["username"]
                        ), tags=(cred["id"],))
                
            except Exception as e:
                messagebox.showerror("错误", f"加载分类数据失败: {str(e)}")
                logger.error(f"加载分类数据失败: {e}")
    
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
                for field, var in self.form_vars.items():
                    if field == 'notes':
                        self.form_entries[field].delete(1.0, tk.END)
                        self.form_entries[field].insert(1.0, cred.get(field, ""))
                    else:
                        var.set(cred.get(field, ""))
            else:
                messagebox.showwarning("警告", result["error"])
                
        except Exception as e:
            messagebox.showerror("错误", f"加载凭据详情失败: {str(e)}")
            logger.error(f"加载凭据详情失败: {e}")
    
    def add_credential(self):
        """新增凭据"""
        self.clear_form()
        self.current_credential_id = None
    
    def save_credential(self):
        """保存凭据"""
        try:
            # 获取表单数据
            form_data = {}
            for field, var in self.form_vars.items():
                if field == 'notes':
                    form_data[field] = self.form_entries[field].get(1.0, tk.END).strip()
                else:
                    form_data[field] = var.get().strip()
            
            # 验证必填字段
            required_fields = ['username', 'account', 'password', 'application']
            for field in required_fields:
                if not form_data[field]:
                    messagebox.showerror("错误", f"请填写{field}")
                    return
            
            if self.current_credential_id:
                # 更新凭据
                result = credential_db.update_credential(self.current_credential_id, **form_data)
                if result["success"]:
                    messagebox.showinfo("成功", "凭据更新成功")
                    self.refresh_data()
                else:
                    messagebox.showerror("错误", result["error"])
            else:
                # 新增凭据
                result = credential_db.add_credential(**form_data)
                if result["success"]:
                    messagebox.showinfo("成功", "凭据添加成功")
                    self.refresh_data()
                    self.clear_form()
                else:
                    messagebox.showerror("错误", result["error"])
                    
        except Exception as e:
            messagebox.showerror("错误", f"保存凭据失败: {str(e)}")
            logger.error(f"保存凭据失败: {e}")
    
    def clear_form(self):
        """清空表单"""
        for field, var in self.form_vars.items():
            if field == 'notes':
                self.form_entries[field].delete(1.0, tk.END)
            else:
                var.set("")
        self.current_credential_id = None
    
    def edit_credential(self):
        """编辑凭据"""
        selection = self.credential_tree.selection()
        if selection:
            item = self.credential_tree.item(selection[0])
            credential_id = int(item['tags'][0])
            self.load_credential_details(credential_id)
    
    def delete_credential(self):
        """删除凭据"""
        if not self.current_credential_id:
            messagebox.showwarning("警告", "请先选择要删除的凭据")
            return
        
        if messagebox.askyesno("确认", "确定要删除这个凭据吗？"):
            try:
                result = credential_db.delete_credential(self.current_credential_id)
                if result["success"]:
                    messagebox.showinfo("成功", "凭据删除成功")
                    self.refresh_data()
                    self.clear_form()
                else:
                    messagebox.showerror("错误", result["error"])
                    
            except Exception as e:
                messagebox.showerror("错误", f"删除凭据失败: {str(e)}")
                logger.error(f"删除凭据失败: {e}")
    
    def copy_account(self):
        """复制账号"""
        if self.current_credential_id:
            result = credential_db.get_credential(self.current_credential_id)
            if result["success"]:
                account = result["credential"]["account"]
                self.root.clipboard_clear()
                self.root.clipboard_append(account)
                messagebox.showinfo("成功", "账号已复制到剪贴板")
    
    def copy_password(self):
        """复制密码"""
        if self.current_credential_id:
            result = credential_db.get_credential(self.current_credential_id)
            if result["success"]:
                password = result["credential"]["password"]
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                messagebox.showinfo("成功", "密码已复制到剪贴板")
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        show = self.show_password_var.get()
        if show:
            self.form_entries['password'].configure(show='')
        else:
            self.form_entries['password'].configure(show='*')
    
    def import_credentials(self):
        """导入凭据"""
        file_path = filedialog.askopenfilename(
            title="选择导入文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                result = credential_db.import_credentials(data)
                if result["success"]:
                    messagebox.showinfo("成功", result["message"])
                    self.refresh_data()
                else:
                    messagebox.showerror("错误", result["error"])
                    
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
                logger.error(f"导入失败: {e}")
    
    def export_credentials(self):
        """导出凭据"""
        file_path = filedialog.asksaveasfilename(
            title="保存导出文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                result = credential_db.export_credentials()
                if result["success"]:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result["data"])
                    messagebox.showinfo("成功", "凭据导出成功")
                else:
                    messagebox.showerror("错误", result["error"])
                    
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
                logger.error(f"导出失败: {e}")
    
    def show_statistics(self):
        """显示统计信息"""
        try:
            # 获取统计信息
            result = credential_db.get_all_credentials()
            categories_result = credential_db.get_application_categories()
            
            if result["success"] and categories_result["success"]:
                credentials = result["credentials"]
                categories = categories_result["categories"]
                
                # 创建统计窗口
                stats_window = tk.Toplevel(self.root)
                stats_window.title("凭据统计")
                stats_window.geometry("500x400")
                stats_window.configure(bg=self.colors['bg_main'])
                
                # 标题
                title_label = tk.Label(stats_window, text="📊 凭据统计", font=('Arial', 16, 'bold'),
                                      bg=self.colors['bg_main'], fg=self.colors['text_primary'])
                title_label.pack(pady=20)
                
                # 统计内容
                stats_frame = tk.Frame(stats_window, bg=self.colors['bg_card'])
                stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
                
                # 总凭据数
                total_label = tk.Label(stats_frame, text=f"总凭据数: {len(credentials)}", 
                                      font=('Arial', 12), bg=self.colors['bg_card'], 
                                      fg=self.colors['text_primary'])
                total_label.pack(pady=10)
                
                # 按应用统计
                app_stats = {}
                for cred in credentials:
                    app = cred["application"]
                    app_stats[app] = app_stats.get(app, 0) + 1
                
                # 应用统计标题
                app_title = tk.Label(stats_frame, text="按应用统计:", font=('Arial', 12, 'bold'),
                                   bg=self.colors['bg_card'], fg=self.colors['text_primary'])
                app_title.pack(pady=(20, 10))
                
                # 应用统计列表
                for app, count in sorted(app_stats.items(), key=lambda x: x[1], reverse=True):
                    app_label = tk.Label(stats_frame, text=f"  {app}: {count} 个凭据", 
                                        font=('Arial', 10), bg=self.colors['bg_card'], 
                                        fg=self.colors['text_secondary'])
                    app_label.pack(anchor=tk.W, padx=20)
                
                # 分类统计标题
                cat_title = tk.Label(stats_frame, text="按分类统计:", font=('Arial', 12, 'bold'),
                                   bg=self.colors['bg_card'], fg=self.colors['text_primary'])
                cat_title.pack(pady=(20, 10))
                
                # 分类统计列表
                for cat in categories:
                    cat_label = tk.Label(stats_frame, text=f"  {cat['category_name']}: {cat['credential_count']} 个凭据", 
                                        font=('Arial', 10), bg=self.colors['bg_card'], 
                                        fg=self.colors['text_secondary'])
                    cat_label.pack(anchor=tk.W, padx=20)
                
            else:
                messagebox.showerror("错误", "获取统计信息失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"显示统计信息失败: {str(e)}")
            logger.error(f"显示统计信息失败: {e}")
    
    def test_auto_fill(self):
        """测试自动填充"""
        # 创建测试窗口
        test_window = tk.Toplevel(self.root)
        test_window.title("自动填充测试")
        test_window.geometry("500x400")
        test_window.configure(bg=self.colors['bg_main'])
        
        # 标题
        title_label = tk.Label(test_window, text="🔍 自动填充测试", font=('Arial', 16, 'bold'),
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        title_label.pack(pady=20)
        
        # 测试表单
        form_frame = tk.Frame(test_window, bg=self.colors['bg_card'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 应用名称
        app_label = tk.Label(form_frame, text="应用名称:", font=('Arial', 12, 'bold'),
                           bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        app_label.pack(anchor=tk.W, pady=(20, 5))
        
        app_var = tk.StringVar()
        app_entry = tk.Entry(form_frame, textvariable=app_var, bg=self.colors['bg_input'], 
                           fg=self.colors['text_primary'], font=('Arial', 11), relief=tk.FLAT, bd=0)
        app_entry.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # 网站URL
        url_label = tk.Label(form_frame, text="网站URL:", font=('Arial', 12, 'bold'),
                           bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        url_label.pack(anchor=tk.W, padx=20)
        
        url_var = tk.StringVar()
        url_entry = tk.Entry(form_frame, textvariable=url_var, bg=self.colors['bg_input'], 
                           fg=self.colors['text_primary'], font=('Arial', 11), relief=tk.FLAT, bd=0)
        url_entry.pack(fill=tk.X, padx=20, pady=(5, 20))
        
        # 测试按钮
        def test_fill():
            app_name = app_var.get().strip()
            website_url = url_var.get().strip()
            
            if not app_name:
                messagebox.showwarning("警告", "请输入应用名称")
                return
            
            result = credential_db.auto_fill_credential(app_name, website_url)
            if result["success"]:
                cred = result["credential"]
                messagebox.showinfo("成功", f"找到凭据:\n用户名: {cred['username']}\n账号: {cred['account']}\n密码: {cred['password']}")
            else:
                messagebox.showinfo("结果", result["error"])
        
        test_btn = tk.Button(form_frame, text="🔍 测试自动填充", command=test_fill,
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           font=('Arial', 12), relief=tk.FLAT, bd=0,
                           activebackground=self.colors['accent_hover'],
                           cursor='hand2', padx=20, pady=10)
        test_btn.pack(pady=20)
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = CredentialManagerUI()
        app.run()
    except Exception as e:
        logger.error(f"UI启动失败: {e}")
        messagebox.showerror("错误", f"UI启动失败: {str(e)}")

if __name__ == "__main__":
    main()
