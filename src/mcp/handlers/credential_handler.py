#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
凭据管理工具处理器
"""

import logging
from typing import Dict, Any
from ..core.base import BaseToolHandler

logger = logging.getLogger(__name__)

class CredentialDatabaseHandler(BaseToolHandler):
    """凭据数据库处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理凭据数据库操作"""
        action = args["action"]
        
        try:
            from src.database.credential_db import credential_db
            
            if action == "add_credential":
                username = args["username"]
                account = args["account"]
                password = args["password"]
                application = args["application"]
                contact = args.get("contact", "")
                website_url = args.get("website_url", "")
                notes = args.get("notes", "")
                result = credential_db.add_credential(username, account, password, application, contact, website_url, notes)
            elif action == "get_credential":
                credential_id = args["credential_id"]
                result = credential_db.get_credential(credential_id)
            elif action == "list_credentials":
                category = args.get("category", None)
                result = credential_db.get_all_credentials(category)
            elif action == "update_credential":
                credential_id = args["credential_id"]
                username = args.get("username")
                account = args.get("account")
                password = args.get("password")
                application = args.get("application")
                contact = args.get("contact")
                website_url = args.get("website_url")
                notes = args.get("notes")
                result = credential_db.update_credential(credential_id, username, account, password, application, contact, website_url, notes)
            elif action == "delete_credential":
                credential_id = args["credential_id"]
                result = credential_db.delete_credential(credential_id)
            elif action == "search_credentials":
                keyword = args["keyword"]
                result = credential_db.search_credentials(keyword)
            elif action == "auto_fill_credential":
                application = args["application"]
                website_url = args.get("website_url", "")
                result = credential_db.auto_fill_credential(application, website_url)
            elif action == "export_credentials":
                file_path = args.get("file_path", "credentials_export.json")
                result = credential_db.export_credentials(file_path)
            elif action == "import_credentials":
                file_path = args["file_path"]
                result = credential_db.import_credentials(file_path)
            elif action == "get_categories":
                result = credential_db.get_application_categories()
            else:
                return {"error": f"不支持的操作: {action}"}
            
            return result
        except Exception as e:
            logger.error(f"凭据数据库操作失败: {e}")
            return {"error": f"凭据数据库操作失败: {str(e)}"}

class AutoFillHandler(BaseToolHandler):
    """自动填充处理器"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理自动填充操作"""
        action = args["action"]
        
        try:
            from src.tools.auto_fill_integration import auto_fill_integration
            
            if action == "auto_fill_website":
                url = args["url"]
                result = auto_fill_integration.auto_fill_for_website(url)
            elif action == "auto_fill_application":
                application = args["application"]
                result = auto_fill_integration.auto_fill_for_application(application)
            elif action == "smart_auto_fill":
                identifier = args["identifier"]
                identifier_type = args.get("identifier_type", "auto")
                result = auto_fill_integration.smart_auto_fill(identifier, identifier_type)
            elif action == "get_suggested_credentials":
                application = args["application"]
                limit = args.get("limit", 5)
                result = auto_fill_integration.get_suggested_credentials(application, limit)
            elif action == "validate_credential_format":
                username = args["username"]
                password = args["password"]
                application = args["application"]
                result = auto_fill_integration.validate_credential_format(username, password, application)
            elif action == "get_auto_fill_statistics":
                result = auto_fill_integration.get_auto_fill_statistics()
            else:
                return {"error": f"不支持的操作: {action}"}
            
            return result
        except Exception as e:
            logger.error(f"自动填充操作失败: {e}")
            return {"error": f"自动填充操作失败: {str(e)}"}


