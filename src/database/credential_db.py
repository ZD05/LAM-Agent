#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import hashlib
import base64
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class CredentialDatabase:
    """用户凭据数据库管理类"""
    
    def __init__(self, db_path: str = "credentials.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建用户凭据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS credentials (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        account TEXT NOT NULL,
                        password TEXT NOT NULL,
                        contact TEXT,
                        application TEXT NOT NULL,
                        website_url TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        UNIQUE(account, application)
                    )
                ''')
                
                # 创建应用分类表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS application_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        icon TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建用户会话表（用于自动填充）
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        application TEXT NOT NULL,
                        website_url TEXT,
                        credential_id INTEGER,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (credential_id) REFERENCES credentials (id)
                    )
                ''')
                
                # 插入默认应用分类
                default_categories = [
                    ('社交软件', '微信、QQ、微博等社交应用', '社交'),
                    ('办公软件', 'WPS、Office、钉钉等办公应用', '办公'),
                    ('电商平台', '淘宝、京东、拼多多等购物平台', '电商'),
                    ('娱乐平台', '抖音、快手、B站等娱乐应用', '娱乐'),
                    ('金融服务', '银行、支付、理财等金融应用', '金融'),
                    ('学习平台', '教育、培训、在线学习平台', '学习'),
                    ('游戏平台', 'Steam、Epic、手游等游戏平台', '游戏'),
                    ('其他', '其他类型的应用', '其他')
                ]
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO application_categories (category_name, description, icon)
                    VALUES (?, ?, ?)
                ''', default_categories)
                
                conn.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def add_credential(self, username: str, account: str, password: str, 
                      application: str, contact: str = "", website_url: str = "", 
                      notes: str = "") -> Dict[str, Any]:
        """添加用户凭据"""
        try:
            # 加密密码
            encrypted_password = self._encrypt_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO credentials (username, account, password, contact, application, website_url, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, account, encrypted_password, contact, application, website_url, notes))
                
                credential_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "success": True,
                    "message": "凭据添加成功",
                    "credential_id": credential_id,
                    "username": username,
                    "account": account,
                    "application": application
                }
                
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": "该账号在此应用中已存在"
            }
        except Exception as e:
            logger.error(f"添加凭据失败: {e}")
            return {
                "success": False,
                "error": f"添加凭据失败: {str(e)}"
            }
    
    def get_credential(self, credential_id: int) -> Dict[str, Any]:
        """获取单个凭据信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, account, password, contact, application, website_url, notes, created_at, updated_at, is_active
                    FROM credentials WHERE id = ? AND is_active = 1
                ''', (credential_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "success": True,
                        "credential": {
                            "id": row[0],
                            "username": row[1],
                            "account": row[2],
                            "password": self._decrypt_password(row[3]),
                            "contact": row[4],
                            "application": row[5],
                            "website_url": row[6],
                            "notes": row[7],
                            "created_at": row[8],
                            "updated_at": row[9],
                            "is_active": bool(row[10])
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "凭据不存在"
                    }
                    
        except Exception as e:
            logger.error(f"获取凭据失败: {e}")
            return {
                "success": False,
                "error": f"获取凭据失败: {str(e)}"
            }
    
    def get_credentials_by_application(self, application: str) -> Dict[str, Any]:
        """根据应用获取凭据列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, account, password, contact, application, website_url, notes, created_at, updated_at
                    FROM credentials WHERE application = ? AND is_active = 1
                    ORDER BY updated_at DESC
                ''', (application,))
                
                rows = cursor.fetchall()
                credentials = []
                
                for row in rows:
                    credentials.append({
                        "id": row[0],
                        "username": row[1],
                        "account": row[2],
                        "password": self._decrypt_password(row[3]),
                        "contact": row[4],
                        "application": row[5],
                        "website_url": row[6],
                        "notes": row[7],
                        "created_at": row[8],
                        "updated_at": row[9]
                    })
                
                return {
                    "success": True,
                    "credentials": credentials,
                    "count": len(credentials)
                }
                
        except Exception as e:
            logger.error(f"获取凭据列表失败: {e}")
            return {
                "success": False,
                "error": f"获取凭据列表失败: {str(e)}"
            }
    
    def get_all_credentials(self, category: str = None) -> Dict[str, Any]:
        """获取所有凭据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('''
                        SELECT c.id, c.username, c.account, c.password, c.contact, c.application, c.website_url, c.notes, c.created_at, c.updated_at
                        FROM credentials c
                        JOIN application_categories ac ON c.application = ac.category_name
                        WHERE ac.category_name = ? AND c.is_active = 1
                        ORDER BY c.updated_at DESC
                    ''', (category,))
                else:
                    cursor.execute('''
                        SELECT id, username, account, password, contact, application, website_url, notes, created_at, updated_at
                        FROM credentials WHERE is_active = 1
                        ORDER BY updated_at DESC
                    ''')
                
                rows = cursor.fetchall()
                credentials = []
                
                for row in rows:
                    credentials.append({
                        "id": row[0],
                        "username": row[1],
                        "account": row[2],
                        "password": self._decrypt_password(row[3]),
                        "contact": row[4],
                        "application": row[5],
                        "website_url": row[6],
                        "notes": row[7],
                        "created_at": row[8],
                        "updated_at": row[9]
                    })
                
                return {
                    "success": True,
                    "credentials": credentials,
                    "count": len(credentials)
                }
                
        except Exception as e:
            logger.error(f"获取所有凭据失败: {e}")
            return {
                "success": False,
                "error": f"获取所有凭据失败: {str(e)}"
            }
    
    def update_credential(self, credential_id: int, **kwargs) -> Dict[str, Any]:
        """更新凭据信息"""
        try:
            # 构建更新字段
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key == 'password':
                    value = self._encrypt_password(value)
                update_fields.append(f"{key} = ?")
                update_values.append(value)
            
            if not update_fields:
                return {
                    "success": False,
                    "error": "没有需要更新的字段"
                }
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(credential_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(f'''
                    UPDATE credentials SET {', '.join(update_fields)}
                    WHERE id = ? AND is_active = 1
                ''', update_values)
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return {
                        "success": True,
                        "message": "凭据更新成功",
                        "credential_id": credential_id
                    }
                else:
                    return {
                        "success": False,
                        "error": "凭据不存在或已被删除"
                    }
                    
        except Exception as e:
            logger.error(f"更新凭据失败: {e}")
            return {
                "success": False,
                "error": f"更新凭据失败: {str(e)}"
            }
    
    def delete_credential(self, credential_id: int) -> Dict[str, Any]:
        """删除凭据（软删除）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE credentials SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND is_active = 1
                ''', (credential_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return {
                        "success": True,
                        "message": "凭据删除成功",
                        "credential_id": credential_id
                    }
                else:
                    return {
                        "success": False,
                        "error": "凭据不存在或已被删除"
                    }
                    
        except Exception as e:
            logger.error(f"删除凭据失败: {e}")
            return {
                "success": False,
                "error": f"删除凭据失败: {str(e)}"
            }
    
    def search_credentials(self, keyword: str) -> Dict[str, Any]:
        """搜索凭据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, account, password, contact, application, website_url, notes, created_at, updated_at
                    FROM credentials 
                    WHERE (username LIKE ? OR account LIKE ? OR application LIKE ? OR notes LIKE ?) 
                    AND is_active = 1
                    ORDER BY updated_at DESC
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
                
                rows = cursor.fetchall()
                credentials = []
                
                for row in rows:
                    credentials.append({
                        "id": row[0],
                        "username": row[1],
                        "account": row[2],
                        "password": self._decrypt_password(row[3]),
                        "contact": row[4],
                        "application": row[5],
                        "website_url": row[6],
                        "notes": row[7],
                        "created_at": row[8],
                        "updated_at": row[9]
                    })
                
                return {
                    "success": True,
                    "credentials": credentials,
                    "count": len(credentials),
                    "keyword": keyword
                }
                
        except Exception as e:
            logger.error(f"搜索凭据失败: {e}")
            return {
                "success": False,
                "error": f"搜索凭据失败: {str(e)}"
            }
    
    def get_application_categories(self) -> Dict[str, Any]:
        """获取应用分类列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT category_name, description, icon, 
                           (SELECT COUNT(*) FROM credentials WHERE application = category_name AND is_active = 1) as credential_count
                    FROM application_categories
                    ORDER BY category_name
                ''')
                
                rows = cursor.fetchall()
                categories = []
                
                for row in rows:
                    categories.append({
                        "category_name": row[0],
                        "description": row[1],
                        "icon": row[2],
                        "credential_count": row[3]
                    })
                
                return {
                    "success": True,
                    "categories": categories,
                    "count": len(categories)
                }
                
        except Exception as e:
            logger.error(f"获取应用分类失败: {e}")
            return {
                "success": False,
                "error": f"获取应用分类失败: {str(e)}"
            }
    
    def auto_fill_credential(self, application: str, website_url: str = "") -> Dict[str, Any]:
        """自动填充凭据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 优先匹配网站URL，然后匹配应用名称
                if website_url:
                    cursor.execute('''
                        SELECT id, username, account, password, contact, notes
                        FROM credentials 
                        WHERE (website_url = ? OR application = ?) AND is_active = 1
                        ORDER BY CASE WHEN website_url = ? THEN 1 ELSE 2 END, updated_at DESC
                        LIMIT 1
                    ''', (website_url, application, website_url))
                else:
                    cursor.execute('''
                        SELECT id, username, account, password, contact, notes
                        FROM credentials 
                        WHERE application = ? AND is_active = 1
                        ORDER BY updated_at DESC
                        LIMIT 1
                    ''', (application,))
                
                row = cursor.fetchone()
                if row:
                    # 更新最后使用时间
                    cursor.execute('''
                        UPDATE credentials SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
                    ''', (row[0],))
                    conn.commit()
                    
                    return {
                        "success": True,
                        "credential": {
                            "id": row[0],
                            "username": row[1],
                            "account": row[2],
                            "password": self._decrypt_password(row[3]),
                            "contact": row[4],
                            "notes": row[5]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"未找到 {application} 的凭据"
                    }
                    
        except Exception as e:
            logger.error(f"自动填充凭据失败: {e}")
            return {
                "success": False,
                "error": f"自动填充凭据失败: {str(e)}"
            }
    
    def _encrypt_password(self, password: str) -> str:
        """加密密码"""
        try:
            # 使用base64编码进行简单加密（实际应用中应使用更强的加密算法）
            encoded = base64.b64encode(password.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception as e:
            logger.error(f"密码加密失败: {e}")
            return password
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """解密密码"""
        try:
            # 使用base64解码
            decoded = base64.b64decode(encrypted_password.encode('utf-8')).decode('utf-8')
            return decoded
        except Exception as e:
            logger.error(f"密码解密失败: {e}")
            return encrypted_password
    
    def export_credentials(self, format: str = "json") -> Dict[str, Any]:
        """导出凭据数据"""
        try:
            result = self.get_all_credentials()
            if not result["success"]:
                return result
            
            credentials = result["credentials"]
            
            if format.lower() == "json":
                export_data = {
                    "export_time": datetime.now().isoformat(),
                    "total_count": len(credentials),
                    "credentials": credentials
                }
                return {
                    "success": True,
                    "data": json.dumps(export_data, ensure_ascii=False, indent=2),
                    "format": "json"
                }
            else:
                return {
                    "success": False,
                    "error": f"不支持的导出格式: {format}"
                }
                
        except Exception as e:
            logger.error(f"导出凭据失败: {e}")
            return {
                "success": False,
                "error": f"导出凭据失败: {str(e)}"
            }
    
    def import_credentials(self, data: str, format: str = "json") -> Dict[str, Any]:
        """导入凭据数据"""
        try:
            if format.lower() == "json":
                import_data = json.loads(data)
                credentials = import_data.get("credentials", [])
            else:
                return {
                    "success": False,
                    "error": f"不支持的导入格式: {format}"
                }
            
            success_count = 0
            error_count = 0
            errors = []
            
            for cred in credentials:
                result = self.add_credential(
                    username=cred.get("username", ""),
                    account=cred.get("account", ""),
                    password=cred.get("password", ""),
                    application=cred.get("application", ""),
                    contact=cred.get("contact", ""),
                    website_url=cred.get("website_url", ""),
                    notes=cred.get("notes", "")
                )
                
                if result["success"]:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"账号 {cred.get('account', '')}: {result.get('error', '')}")
            
            return {
                "success": True,
                "message": f"导入完成，成功: {success_count}, 失败: {error_count}",
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"导入凭据失败: {e}")
            return {
                "success": False,
                "error": f"导入凭据失败: {str(e)}"
            }

# 全局数据库实例
credential_db = CredentialDatabase()
