#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import requests
import webbrowser
import subprocess
import winreg
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class SteamIntegration:
    """Steam集成类，提供Steam游戏库和统计信息功能"""
    
    def __init__(self):
        self.steam_api_key = os.getenv('STEAM_API_KEY', '')
        self.steam_user_id = os.getenv('STEAM_USER_ID', '')
        self.base_url = "https://api.steampowered.com"
        self.store_url = "https://store.steampowered.com"
        self.steam_paths = []
    
    def find_steam_comprehensive(self) -> List[str]:
        """全面查找Steam安装路径"""
        paths = []
        
        # 1. 检查注册表
        try:
            logger.info("检查注册表...")
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
            ]
            
            for hkey, subkey in reg_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                        steam_exe = os.path.join(install_path, "steam.exe")
                        if os.path.exists(steam_exe):
                            paths.append(steam_exe)
                            logger.info(f"从注册表找到Steam: {steam_exe}")
                except Exception as e:
                    logger.debug(f"注册表检查失败: {e}")
        except Exception as e:
            logger.warning(f"注册表检查出错: {e}")
        
        # 2. 检查常见安装路径
        common_paths = [
            r"C:\Program Files (x86)\Steam\steam.exe",
            r"C:\Program Files\Steam\steam.exe",
            r"D:\Steam\steam.exe",
            r"E:\Steam\steam.exe",
            r"F:\Steam\steam.exe",
            r"C:\Games\Steam\steam.exe",
            r"D:\Games\Steam\steam.exe",
            r"E:\Games\Steam\steam.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                paths.append(path)
                logger.info(f"找到Steam: {path}")
        
        # 3. 检查桌面快捷方式
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if os.path.exists(desktop_path):
                for item in os.listdir(desktop_path):
                    if 'steam' in item.lower() and item.endswith('.lnk'):
                        shortcut_path = os.path.join(desktop_path, item)
                        try:
                            import win32com.client
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortCut(shortcut_path)
                            target_path = shortcut.Targetpath
                            if target_path and os.path.exists(target_path):
                                paths.append(target_path)
                                logger.info(f"从桌面快捷方式找到Steam: {target_path}")
                        except Exception as e:
                            logger.debug(f"解析快捷方式失败: {e}")
        except Exception as e:
            logger.warning(f"检查桌面快捷方式出错: {e}")
        
        # 4. 检查开始菜单
        try:
            start_menu_paths = [
                os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs"),
                os.path.join(os.environ.get('PROGRAMDATA', ''), r"Microsoft\Windows\Start Menu\Programs")
            ]
            
            for start_menu in start_menu_paths:
                if os.path.exists(start_menu):
                    for root, dirs, files in os.walk(start_menu):
                        for file in files:
                            if 'steam' in file.lower() and file.endswith('.lnk'):
                                shortcut_path = os.path.join(root, file)
                                try:
                                    import win32com.client
                                    shell = win32com.client.Dispatch("WScript.Shell")
                                    shortcut = shell.CreateShortCut(shortcut_path)
                                    target_path = shortcut.Targetpath
                                    if target_path and os.path.exists(target_path):
                                        paths.append(target_path)
                                        logger.info(f"从开始菜单找到Steam: {target_path}")
                                except Exception as e:
                                    logger.debug(f"解析开始菜单快捷方式失败: {e}")
        except Exception as e:
            logger.warning(f"检查开始菜单出错: {e}")
        
        # 去重
        unique_paths = list(set(paths))
        self.steam_paths = unique_paths
        return unique_paths
    
    def safe_launch_steam(self) -> Dict[str, Any]:
        """安全启动Steam，避免黑屏问题"""
        try:
            # 查找Steam
            steam_paths = self.find_steam_comprehensive()
            
            if not steam_paths:
                return {
                    'success': False,
                    'error': '未找到Steam安装',
                    'suggestion': '请确保Steam已正确安装，或手动指定Steam路径'
                }
            
            # 使用第一个找到的Steam路径
            steam_path = steam_paths[0]
            logger.info(f"使用Steam路径: {steam_path}")
            
            # 使用os.startfile安全启动
            os.startfile(steam_path)
            
            # 等待启动
            time.sleep(3)
            
            return {
                'success': True,
                'steam_path': steam_path,
                'message': 'Steam启动成功'
            }
            
        except Exception as e:
            logger.error(f"启动Steam失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def wait_for_steam_ui(self, timeout: int = 30) -> bool:
        """等待Steam UI加载完成"""
        logger.info("等待Steam UI加载...")
        
        for i in range(timeout):
            try:
                # 检查Steam进程是否运行
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq steam.exe'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if 'steam.exe' in result.stdout:
                    logger.info("Steam进程已启动")
                    time.sleep(3)  # 额外等待UI加载
                    return True
                    
            except Exception as e:
                logger.warning(f"检查Steam进程时出错: {e}")
            
            time.sleep(1)
        
        logger.warning("Steam UI加载超时")
        return False
        
    def get_game_library(self) -> Dict[str, Any]:
        """获取游戏库信息"""
        try:
            if not self.steam_api_key or not self.steam_user_id:
                return {
                    "success": False,
                    "error": "Steam API密钥或用户ID未配置",
                    "message": "请在环境变量中设置 STEAM_API_KEY 和 STEAM_USER_ID"
                }
            
            # 获取用户游戏库
            url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"
            params = {
                'key': self.steam_api_key,
                'steamid': self.steam_user_id,
                'format': 'json',
                'include_appinfo': True,
                'include_played_free_games': True
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            games = data.get('response', {}).get('games', [])
            
            # 处理游戏信息
            processed_games = []
            total_playtime = 0
            
            for game in games:
                game_info = {
                    'appid': game.get('appid'),
                    'name': game.get('name', 'Unknown'),
                    'playtime_forever': game.get('playtime_forever', 0),
                    'playtime_2weeks': game.get('playtime_2weeks', 0),
                    'playtime_windows_forever': game.get('playtime_windows_forever', 0),
                    'playtime_mac_forever': game.get('playtime_mac_forever', 0),
                    'playtime_linux_forever': game.get('playtime_linux_forever', 0),
                    'last_played': game.get('rtime_last_played', 0),
                    'icon_url': game.get('img_icon_url', ''),
                    'logo_url': game.get('img_logo_url', ''),
                    'has_community_visible_stats': game.get('has_community_visible_stats', False)
                }
                
                processed_games.append(game_info)
                total_playtime += game_info['playtime_forever']
            
            # 按游戏时长排序
            processed_games.sort(key=lambda x: x['playtime_forever'], reverse=True)
            
            return {
                "success": True,
                "total_games": len(processed_games),
                "total_playtime_minutes": total_playtime,
                "total_playtime_hours": round(total_playtime / 60, 2),
                "games": processed_games[:20],  # 返回前20个游戏
                "message": f"成功获取 {len(processed_games)} 个游戏"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Steam API请求失败: {e}")
            return {
                "success": False,
                "error": f"Steam API请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"获取游戏库失败: {e}")
            return {
                "success": False,
                "error": f"获取游戏库失败: {str(e)}"
            }
    
    def get_recent_activity(self) -> Dict[str, Any]:
        """获取最近的游戏活动"""
        try:
            if not self.steam_api_key or not self.steam_user_id:
                return {
                    "success": False,
                    "error": "Steam API密钥或用户ID未配置"
                }
            
            # 获取最近游戏活动
            url = f"{self.base_url}/IPlayerService/GetRecentlyPlayedGames/v0001/"
            params = {
                'key': self.steam_api_key,
                'steamid': self.steam_user_id,
                'format': 'json',
                'count': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            recent_games = data.get('response', {}).get('games', [])
            
            # 处理最近游戏信息
            processed_games = []
            for game in recent_games:
                last_played = game.get('rtime_last_played', 0)
                game_info = {
                    'appid': game.get('appid'),
                    'name': game.get('name', 'Unknown'),
                    'playtime_2weeks': game.get('playtime_2weeks', 0),
                    'playtime_forever': game.get('playtime_forever', 0),
                    'last_played': last_played,
                    'last_played_date': datetime.fromtimestamp(last_played).strftime('%Y-%m-%d %H:%M:%S') if last_played else 'Never',
                    'icon_url': game.get('img_icon_url', ''),
                    'logo_url': game.get('img_logo_url', '')
                }
                processed_games.append(game_info)
            
            return {
                "success": True,
                "recent_games": processed_games,
                "count": len(processed_games),
                "message": f"成功获取 {len(processed_games)} 个最近游戏"
            }
            
        except Exception as e:
            logger.error(f"获取最近活动失败: {e}")
            return {
                "success": False,
                "error": f"获取最近活动失败: {str(e)}"
            }
    
    def get_game_details(self, appid: str) -> Dict[str, Any]:
        """获取游戏详细信息"""
        try:
            if not self.steam_api_key:
                return {
                    "success": False,
                    "error": "Steam API密钥未配置"
                }
            
            # 获取游戏详细信息
            url = f"{self.base_url}/ISteamUserStats/GetSchemaForGame/v2/"
            params = {
                'key': self.steam_api_key,
                'appid': appid
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            game_data = data.get('game', {})
            
            # 获取游戏成就
            achievements = []
            if 'availableGameStats' in game_data and 'achievements' in game_data['availableGameStats']:
                for achievement in game_data['availableGameStats']['achievements']:
                    achievements.append({
                        'name': achievement.get('name', ''),
                        'displayName': achievement.get('displayName', ''),
                        'description': achievement.get('description', ''),
                        'icon': achievement.get('icon', ''),
                        'icongray': achievement.get('icongray', '')
                    })
            
            # 获取游戏统计
            stats = []
            if 'availableGameStats' in game_data and 'stats' in game_data['availableGameStats']:
                for stat in game_data['availableGameStats']['stats']:
                    stats.append({
                        'name': stat.get('name', ''),
                        'displayName': stat.get('displayName', ''),
                        'type': stat.get('type', ''),
                        'defaultvalue': stat.get('defaultvalue', 0)
                    })
            
            return {
                "success": True,
                "appid": appid,
                "gameName": game_data.get('gameName', 'Unknown'),
                "gameVersion": game_data.get('gameVersion', ''),
                "achievements": achievements,
                "stats": stats,
                "achievement_count": len(achievements),
                "stats_count": len(stats),
                "message": f"成功获取游戏 {appid} 的详细信息"
            }
            
        except Exception as e:
            logger.error(f"获取游戏详情失败: {e}")
            return {
                "success": False,
                "error": f"获取游戏详情失败: {str(e)}"
            }
    
    def get_friend_comparison(self) -> Dict[str, Any]:
        """获取朋友游戏库比较"""
        try:
            if not self.steam_api_key or not self.steam_user_id:
                return {
                    "success": False,
                    "error": "Steam API密钥或用户ID未配置"
                }
            
            # 获取朋友列表
            url = f"{self.base_url}/ISteamUser/GetFriendList/v0001/"
            params = {
                'key': self.steam_api_key,
                'steamid': self.steam_user_id,
                'relationship': 'friend',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            friends = data.get('friendslist', {}).get('friends', [])
            
            # 获取朋友游戏库（限制前5个朋友）
            friend_games = []
            for friend in friends[:5]:
                friend_id = friend.get('steamid')
                friend_games_url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"
                friend_params = {
                    'key': self.steam_api_key,
                    'steamid': friend_id,
                    'format': 'json',
                    'include_appinfo': True
                }
                
                try:
                    friend_response = requests.get(friend_games_url, params=friend_params, timeout=5)
                    friend_response.raise_for_status()
                    friend_data = friend_response.json()
                    friend_games_list = friend_data.get('response', {}).get('games', [])
                    
                    friend_games.append({
                        'steamid': friend_id,
                        'games_count': len(friend_games_list),
                        'games': [game.get('name', 'Unknown') for game in friend_games_list[:10]]
                    })
                except:
                    continue
            
            return {
                "success": True,
                "friends_count": len(friends),
                "friend_games": friend_games,
                "message": f"成功获取 {len(friends)} 个朋友的游戏库信息"
            }
            
        except Exception as e:
            logger.error(f"获取朋友比较失败: {e}")
            return {
                "success": False,
                "error": f"获取朋友比较失败: {str(e)}"
            }
    
    def analyze_gaming_habits(self) -> Dict[str, Any]:
        """分析游戏习惯和偏好"""
        try:
            # 获取游戏库数据
            library_data = self.get_game_library()
            if not library_data.get('success'):
                return library_data
            
            games = library_data.get('games', [])
            if not games:
                return {
                    "success": False,
                    "error": "没有游戏数据可供分析"
                }
            
            # 分析游戏类型偏好
            game_types = {}
            total_playtime = 0
            
            for game in games:
                playtime = game.get('playtime_forever', 0)
                total_playtime += playtime
                
                # 简单的游戏类型分类（基于游戏名称）
                name = game.get('name', '').lower()
                if any(keyword in name for keyword in ['fps', 'shooter', 'action']):
                    game_types['动作/射击'] = game_types.get('动作/射击', 0) + playtime
                elif any(keyword in name for keyword in ['rpg', 'role', 'adventure']):
                    game_types['角色扮演/冒险'] = game_types.get('角色扮演/冒险', 0) + playtime
                elif any(keyword in name for keyword in ['strategy', 'tactics', 'simulation']):
                    game_types['策略/模拟'] = game_types.get('策略/模拟', 0) + playtime
                elif any(keyword in name for keyword in ['racing', 'sports', 'fitness']):
                    game_types['竞速/体育'] = game_types.get('竞速/体育', 0) + playtime
                else:
                    game_types['其他'] = game_types.get('其他', 0) + playtime
            
            # 计算百分比
            type_percentages = {}
            for game_type, playtime in game_types.items():
                if total_playtime > 0:
                    type_percentages[game_type] = round((playtime / total_playtime) * 100, 2)
            
            # 找出最常玩的游戏
            top_games = sorted(games, key=lambda x: x.get('playtime_forever', 0), reverse=True)[:5]
            
            # 分析游戏时长分布
            playtime_ranges = {
                '0-10小时': 0,
                '10-50小时': 0,
                '50-100小时': 0,
                '100-500小时': 0,
                '500小时以上': 0
            }
            
            for game in games:
                playtime = game.get('playtime_forever', 0)
                if playtime < 10:
                    playtime_ranges['0-10小时'] += 1
                elif playtime < 50:
                    playtime_ranges['10-50小时'] += 1
                elif playtime < 100:
                    playtime_ranges['50-100小时'] += 1
                elif playtime < 500:
                    playtime_ranges['100-500小时'] += 1
                else:
                    playtime_ranges['500小时以上'] += 1
            
            return {
                "success": True,
                "total_games": len(games),
                "total_playtime_hours": round(total_playtime / 60, 2),
                "game_type_preferences": type_percentages,
                "top_games": [
                    {
                        'name': game.get('name'),
                        'playtime_hours': round(game.get('playtime_forever', 0) / 60, 2)
                    } for game in top_games
                ],
                "playtime_distribution": playtime_ranges,
                "analysis_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "message": "游戏习惯分析完成"
            }
            
        except Exception as e:
            logger.error(f"分析游戏习惯失败: {e}")
            return {
                "success": False,
                "error": f"分析游戏习惯失败: {str(e)}"
            }
    
    def open_steam_store(self, game_name: str = "") -> Dict[str, Any]:
        """打开Steam商店"""
        try:
            # 使用新的安全启动方法
            launch_result = self.safe_launch_steam()
            
            if not launch_result.get('success'):
                return launch_result
            
            # 等待Steam UI加载
            if not self.wait_for_steam_ui():
                return {
                    'success': False,
                    'error': 'Steam UI加载超时'
                }
            
            # 如果指定了游戏名称，尝试打开游戏页面
            if game_name:
                try:
                    # 使用Steam URL协议打开游戏页面
                    game_url = f"steam://store/{game_name}"
                    os.startfile(game_url)
                    return {
                        "success": True,
                        "message": f"Steam启动成功，正在打开游戏页面: {game_name}",
                        "method": "steam_url",
                        "game_url": game_url
                    }
                except Exception as e:
                    logger.warning(f"打开游戏页面失败: {e}")
                    # 继续执行，至少Steam已经启动
            
            return {
                "success": True,
                "message": "Steam启动成功",
                "method": "safe_launch",
                "steam_path": launch_result.get('steam_path')
            }
                
        except Exception as e:
            logger.error(f"打开Steam商店失败: {e}")
            return {
                "success": False,
                "error": f"打开Steam商店失败: {str(e)}"
            }
    
    def get_game_recommendations(self) -> Dict[str, Any]:
        """获取游戏推荐"""
        try:
            # 获取游戏库进行分析
            library_data = self.get_game_library()
            if not library_data.get('success'):
                return library_data
            
            games = library_data.get('games', [])
            if not games:
                return {
                    "success": False,
                    "error": "没有游戏数据可供推荐"
                }
            
            # 基于游戏类型推荐（模拟推荐逻辑）
            recommendations = []
            
            # 分析现有游戏类型
            game_types = set()
            for game in games[:10]:  # 分析前10个游戏
                name = game.get('name', '').lower()
                if any(keyword in name for keyword in ['fps', 'shooter']):
                    game_types.add('射击游戏')
                elif any(keyword in name for keyword in ['rpg', 'role']):
                    game_types.add('角色扮演')
                elif any(keyword in name for keyword in ['strategy', 'tactics']):
                    game_types.add('策略游戏')
                elif any(keyword in name for keyword in ['racing', 'sports']):
                    game_types.add('竞速体育')
            
            # 生成推荐
            if '射击游戏' in game_types:
                recommendations.append({
                    'name': 'Counter-Strike 2',
                    'reason': '基于您对射击游戏的偏好',
                    'category': '射击游戏'
                })
            
            if '角色扮演' in game_types:
                recommendations.append({
                    'name': 'The Witcher 3: Wild Hunt',
                    'reason': '基于您对角色扮演游戏的偏好',
                    'category': '角色扮演'
                })
            
            if '策略游戏' in game_types:
                recommendations.append({
                    'name': 'Civilization VI',
                    'reason': '基于您对策略游戏的偏好',
                    'category': '策略游戏'
                })
            
            # 添加一些通用推荐
            recommendations.extend([
                {
                    'name': 'Portal 2',
                    'reason': '经典解谜游戏，评分极高',
                    'category': '解谜游戏'
                },
                {
                    'name': 'Stardew Valley',
                    'reason': '轻松休闲的农场模拟游戏',
                    'category': '模拟游戏'
                }
            ])
            
            return {
                "success": True,
                "recommendations": recommendations[:5],
                "based_on_games": len(games),
                "message": f"基于您的 {len(games)} 个游戏生成了推荐"
            }
            
        except Exception as e:
            logger.error(f"获取游戏推荐失败: {e}")
            return {
                "success": False,
                "error": f"获取游戏推荐失败: {str(e)}"
            }
    
    def download_game(self, appid: str) -> Dict[str, Any]:
        """下载游戏"""
        try:
            import subprocess
            
            # 获取Steam安装路径
            steam_exe_path = self._get_steam_exe_path()
            if not steam_exe_path:
                return {
                    "success": False,
                    "error": "未找到Steam安装路径"
                }
            
            # 使用Steam命令行下载游戏
            # Steam命令行格式: steam://install/appid
            download_url = f"steam://install/{appid}"
            
            try:
                # 使用start命令打开Steam下载链接
                subprocess.run(["start", "", download_url], shell=True, check=True, timeout=5)
                return {
                    "success": True,
                    "message": f"已开始下载游戏 (AppID: {appid})",
                    "appid": appid,
                    "download_url": download_url,
                    "method": "steam_command"
                }
            except subprocess.CalledProcessError:
                # 如果命令行失败，尝试在浏览器中打开
                webbrowser.open(f"https://store.steampowered.com/app/{appid}")
                return {
                    "success": True,
                    "message": f"在浏览器中打开游戏页面 (AppID: {appid})",
                    "appid": appid,
                    "url": f"https://store.steampowered.com/app/{appid}",
                    "method": "browser_fallback"
                }
                
        except Exception as e:
            logger.error(f"下载游戏失败: {e}")
            return {
                "success": False,
                "error": f"下载游戏失败: {str(e)}"
            }
    
    def uninstall_game(self, appid: str) -> Dict[str, Any]:
        """卸载游戏"""
        try:
            import subprocess
            
            # 获取Steam安装路径
            steam_exe_path = self._get_steam_exe_path()
            if not steam_exe_path:
                return {
                    "success": False,
                    "error": "未找到Steam安装路径"
                }
            
            # 使用Steam命令行卸载游戏
            # Steam命令行格式: steam://uninstall/appid
            uninstall_url = f"steam://uninstall/{appid}"
            
            try:
                # 使用start命令打开Steam卸载链接
                subprocess.run(["start", "", uninstall_url], shell=True, check=True, timeout=5)
                return {
                    "success": True,
                    "message": f"已开始卸载游戏 (AppID: {appid})",
                    "appid": appid,
                    "uninstall_url": uninstall_url,
                    "method": "steam_command"
                }
            except subprocess.CalledProcessError:
                # 如果命令行失败，尝试在浏览器中打开
                webbrowser.open(f"https://store.steampowered.com/app/{appid}")
                return {
                    "success": True,
                    "message": f"在浏览器中打开游戏页面 (AppID: {appid})",
                    "appid": appid,
                    "url": f"https://store.steampowered.com/app/{appid}",
                    "method": "browser_fallback"
                }
                
        except Exception as e:
            logger.error(f"卸载游戏失败: {e}")
            return {
                "success": False,
                "error": f"卸载游戏失败: {str(e)}"
            }
    
    def _get_steam_exe_path(self) -> str:
        """获取Steam可执行文件路径"""
        try:
            import winreg
            
            # 从注册表获取Steam安装路径
            registry_paths = [
                r"SOFTWARE\Valve\Steam",
                r"SOFTWARE\WOW6432Node\Valve\Steam",
            ]
            
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    steam_exe_path = os.path.join(install_path, "steam.exe")
                    winreg.CloseKey(key)
                    
                    if os.path.exists(steam_exe_path):
                        return steam_exe_path
                except (FileNotFoundError, OSError):
                    continue
            
            # 尝试常见安装路径
            common_paths = [
                "C:/Program Files (x86)/Steam/steam.exe",
                "C:/Program Files/Steam/steam.exe",
                "D:/Program Files (x86)/Steam/steam.exe",
                "D:/Program Files/Steam/steam.exe",
                "E:/Program Files (x86)/Steam/steam.exe",
                "E:/Program Files/Steam/steam.exe",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
                    
        except ImportError:
            # Linux/Mac系统没有winreg
            pass
        except Exception as e:
            logger.warning(f"获取Steam路径失败: {e}")
        
        return None

# 全局Steam集成实例
steam_integration = SteamIntegration()
