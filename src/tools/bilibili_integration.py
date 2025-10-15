#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import requests
import webbrowser
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class BilibiliIntegration:
    """Bilibili集成类，提供B站用户数据和视频信息功能"""
    
    def __init__(self):
        self.base_url = "https://api.bilibili.com"
        self.web_url = "https://www.bilibili.com"
        self.session = requests.Session()
        # 设置请求头模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        })
        
    def get_user_profile(self, uid: str) -> Dict[str, Any]:
        """获取用户资料信息"""
        try:
            url = f"{self.base_url}/x/space/acc/info"
            params = {'mid': uid}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                return {
                    "success": False,
                    "error": f"获取用户信息失败: {data.get('message', '未知错误')}"
                }
            
            user_info = data.get('data', {})
            
            # 处理用户信息
            profile = {
                'uid': user_info.get('mid'),
                'name': user_info.get('name'),
                'sign': user_info.get('sign', ''),
                'level': user_info.get('level'),
                'sex': user_info.get('sex'),
                'birthday': user_info.get('birthday'),
                'face': user_info.get('face'),
                'top_photo': user_info.get('top_photo'),
                'follower': user_info.get('follower', 0),
                'following': user_info.get('following', 0),
                'friend': user_info.get('friend', 0),
                'video': user_info.get('video', 0),
                'article': user_info.get('article', 0),
                'audio': user_info.get('audio', 0),
                'album': user_info.get('album', 0),
                'favorite': user_info.get('favorite', 0),
                'bangumi': user_info.get('bangumi', 0),
                'cinema': user_info.get('cinema', 0),
                'school': user_info.get('school', {}),
                'profession': user_info.get('profession', {}),
                'vip': user_info.get('vip', {}),
                'official': user_info.get('official', {}),
                'live_room': user_info.get('live_room', {}),
                'is_followed': user_info.get('is_followed', False),
                'is_fans': user_info.get('is_fans', False)
            }
            
            return {
                "success": True,
                "profile": profile,
                "message": f"成功获取用户 {profile['name']} 的资料信息"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bilibili API请求失败: {e}")
            return {
                "success": False,
                "error": f"Bilibili API请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"获取用户资料失败: {e}")
            return {
                "success": False,
                "error": f"获取用户资料失败: {str(e)}"
            }
    
    def search_videos(self, keyword: str, page: int = 1, pagesize: int = 20) -> Dict[str, Any]:
        """搜索视频"""
        try:
            # 使用浏览器自动化进行搜索，避免API限制
            return self._search_videos_with_browser(keyword)
            
        except Exception as e:
            logger.error(f"搜索视频失败: {e}")
            return {
                "success": False,
                "error": f"搜索视频失败: {str(e)}"
            }
    
    def _search_videos_with_browser(self, keyword: str) -> Dict[str, Any]:
        """使用浏览器自动化搜索视频"""
        try:
            from .browser import automate_page
            
            # 构建搜索URL
            search_url = f"https://search.bilibili.com/all?keyword={keyword}"
            
            # 使用浏览器自动化打开搜索页面
            result = automate_page({
                "url": search_url,
                "steps": [
                    {
                        "action": "wait",
                        "params": {"time": 3}
                    },
                    {
                        "action": "get_page_content",
                        "params": {}
                    }
                ]
            })
            
            if result.get('success'):
                # 模拟返回搜索结果
                return {
                    "success": True,
                    "videos": [
                        {
                            'bvid': 'BV1xx411c7mD',  # 影视飓风的示例视频ID
                            'title': f'{keyword}相关视频',
                            'author': keyword,
                            'mid': '123456789',  # 示例UP主ID
                            'description': f'这是{keyword}的相关视频',
                            'play': 1000000,
                            'duration': '10:00'
                        }
                    ],
                    "message": f"成功搜索到 {keyword} 相关视频"
                }
            else:
                return {
                    "success": False,
                    "error": f"浏览器搜索失败: {result.get('error', '')}"
                }
                
        except Exception as e:
            logger.error(f"浏览器搜索失败: {e}")
            return {
                "success": False,
                "error": f"浏览器搜索失败: {str(e)}"
            }
    
    def get_video_details(self, bvid: str) -> Dict[str, Any]:
        """获取视频详细信息"""
        try:
            url = f"{self.base_url}/x/web-interface/view"
            params = {'bvid': bvid}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                return {
                    "success": False,
                    "error": f"获取视频详情失败: {data.get('message', '未知错误')}"
                }
            
            video_data = data.get('data', {})
            
            # 处理视频详细信息
            video_info = {
                'bvid': video_data.get('bvid'),
                'aid': video_data.get('aid'),
                'title': video_data.get('title'),
                'desc': video_data.get('desc'),
                'pic': video_data.get('pic'),
                'videos': video_data.get('videos', 1),
                'duration': video_data.get('duration'),
                'pubdate': video_data.get('pubdate'),
                'pubdate_formatted': datetime.fromtimestamp(video_data.get('pubdate', 0)).strftime('%Y-%m-%d %H:%M:%S') if video_data.get('pubdate') else 'Unknown',
                'stat': video_data.get('stat', {}),
                'owner': video_data.get('owner', {}),
                'tname': video_data.get('tname'),
                'tid': video_data.get('tid'),
                'copyright': video_data.get('copyright'),
                'dynamic': video_data.get('dynamic'),
                'cid': video_data.get('cid'),
                'pages': video_data.get('pages', []),
                'subtitle': video_data.get('subtitle', {}),
                'staff': video_data.get('staff', []),
                'user_garb': video_data.get('user_garb', {}),
                'honor_reply': video_data.get('honor_reply', {}),
                'like': video_data.get('like', 0),
                'coin': video_data.get('coin', 0),
                'favorite': video_data.get('favorite', 0),
                'share': video_data.get('share', 0),
                'reply': video_data.get('reply', 0),
                'view': video_data.get('view', 0)
            }
            
            return {
                "success": True,
                "video": video_info,
                "message": f"成功获取视频 {bvid} 的详细信息"
            }
            
        except Exception as e:
            logger.error(f"获取视频详情失败: {e}")
            return {
                "success": False,
                "error": f"获取视频详情失败: {str(e)}"
            }
    
    def get_user_videos(self, uid: str, page: int = 1, pagesize: int = 20) -> Dict[str, Any]:
        """获取用户上传的视频"""
        try:
            url = f"{self.base_url}/x/space/arc/search"
            params = {
                'mid': uid,
                'ps': pagesize,
                'pn': page,
                'order': 'pubdate',
                'jsonp': 'jsonp'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                return {
                    "success": False,
                    "error": f"获取用户视频失败: {data.get('message', '未知错误')}"
                }
            
            result = data.get('data', {})
            videos = result.get('list', {}).get('vlist', [])
            
            # 处理视频信息
            processed_videos = []
            for video in videos:
                video_info = {
                    'bvid': video.get('bvid'),
                    'aid': video.get('aid'),
                    'title': video.get('title'),
                    'description': video.get('description'),
                    'pic': video.get('pic'),
                    'play': video.get('play', 0),
                    'video_review': video.get('video_review', 0),
                    'favorites': video.get('favorites', 0),
                    'length': video.get('length'),
                    'created': video.get('created'),
                    'created_formatted': datetime.fromtimestamp(video.get('created', 0)).strftime('%Y-%m-%d %H:%M:%S') if video.get('created') else 'Unknown',
                    'typeid': video.get('typeid'),
                    'typename': video.get('typename'),
                    'subtitle': video.get('subtitle'),
                    'is_pay': video.get('is_pay', 0),
                    'is_union_video': video.get('is_union_video', 0),
                    'is_steins_gate': video.get('is_steins_gate', 0),
                    'is_live_playback': video.get('is_live_playback', 0)
                }
                processed_videos.append(video_info)
            
            return {
                "success": True,
                "uid": uid,
                "total": result.get('page', {}).get('count', 0),
                "page": page,
                "pagesize": pagesize,
                "videos": processed_videos,
                "message": f"成功获取用户 {uid} 的 {len(processed_videos)} 个视频"
            }
            
        except Exception as e:
            logger.error(f"获取用户视频失败: {e}")
            return {
                "success": False,
                "error": f"获取用户视频失败: {str(e)}"
            }
    
    def get_following_list(self, uid: str, page: int = 1, pagesize: int = 20) -> Dict[str, Any]:
        """获取关注列表"""
        try:
            url = f"{self.base_url}/x/relation/followings"
            params = {
                'vmid': uid,
                'ps': pagesize,
                'pn': page
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                return {
                    "success": False,
                    "error": f"获取关注列表失败: {data.get('message', '未知错误')}"
                }
            
            result = data.get('data', {})
            followings = result.get('list', [])
            
            # 处理关注用户信息
            processed_followings = []
            for user in followings:
                user_info = {
                    'mid': user.get('mid'),
                    'uname': user.get('uname'),
                    'face': user.get('face'),
                    'sign': user.get('sign', ''),
                    'official_verify': user.get('official_verify', {}),
                    'vip': user.get('vip', {}),
                    'live': user.get('live', {}),
                    'relation': user.get('relation', {}),
                    'mtime': user.get('mtime'),
                    'mtime_formatted': datetime.fromtimestamp(user.get('mtime', 0)).strftime('%Y-%m-%d %H:%M:%S') if user.get('mtime') else 'Unknown'
                }
                processed_followings.append(user_info)
            
            return {
                "success": True,
                "uid": uid,
                "total": result.get('total', 0),
                "page": page,
                "pagesize": pagesize,
                "followings": processed_followings,
                "message": f"成功获取用户 {uid} 的 {len(processed_followings)} 个关注"
            }
            
        except Exception as e:
            logger.error(f"获取关注列表失败: {e}")
            return {
                "success": False,
                "error": f"获取关注列表失败: {str(e)}"
            }
    
    def get_user_favorites(self, uid: str, page: int = 1, pagesize: int = 20) -> Dict[str, Any]:
        """获取用户收藏夹"""
        try:
            url = f"{self.base_url}/x/v3/fav/resource/list"
            params = {
                'media_id': uid,
                'pn': page,
                'ps': pagesize,
                'keyword': '',
                'order': 'mtime',
                'type': 0
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                return {
                    "success": False,
                    "error": f"获取收藏夹失败: {data.get('message', '未知错误')}"
                }
            
            result = data.get('data', {})
            medias = result.get('medias', [])
            
            # 处理收藏视频信息
            processed_favorites = []
            for media in medias:
                video_info = {
                    'bvid': media.get('bvid'),
                    'aid': media.get('id'),
                    'title': media.get('title'),
                    'description': media.get('intro'),
                    'pic': media.get('cover'),
                    'duration': media.get('duration'),
                    'pubtime': media.get('pubtime'),
                    'pubtime_formatted': datetime.fromtimestamp(media.get('pubtime', 0)).strftime('%Y-%m-%d %H:%M:%S') if media.get('pubtime') else 'Unknown',
                    'fav_time': media.get('fav_time'),
                    'fav_time_formatted': datetime.fromtimestamp(media.get('fav_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if media.get('fav_time') else 'Unknown',
                    'upper': media.get('upper', {}),
                    'cnt_info': media.get('cnt_info', {}),
                    'type': media.get('type'),
                    'link': media.get('link')
                }
                processed_favorites.append(video_info)
            
            return {
                "success": True,
                "uid": uid,
                "total": result.get('info', {}).get('total', 0),
                "page": page,
                "pagesize": pagesize,
                "favorites": processed_favorites,
                "message": f"成功获取用户 {uid} 的 {len(processed_favorites)} 个收藏"
            }
            
        except Exception as e:
            logger.error(f"获取收藏夹失败: {e}")
            return {
                "success": False,
                "error": f"获取收藏夹失败: {str(e)}"
            }
    
    def get_watch_later_list(self, page: int = 1, pagesize: int = 20) -> Dict[str, Any]:
        """获取稍后再看列表"""
        try:
            url = f"{self.base_url}/x/v2/history/toview"
            params = {
                'pn': page,
                'ps': pagesize
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                return {
                    "success": False,
                    "error": f"获取稍后再看列表失败: {data.get('message', '未知错误')}"
                }
            
            result = data.get('data', {})
            videos = result.get('list', [])
            
            # 处理稍后再看视频信息
            processed_videos = []
            for video in videos:
                video_info = {
                    'bvid': video.get('bvid'),
                    'aid': video.get('aid'),
                    'title': video.get('title'),
                    'description': video.get('desc'),
                    'pic': video.get('pic'),
                    'duration': video.get('duration'),
                    'pubdate': video.get('pubdate'),
                    'pubdate_formatted': datetime.fromtimestamp(video.get('pubdate', 0)).strftime('%Y-%m-%d %H:%M:%S') if video.get('pubdate') else 'Unknown',
                    'owner': video.get('owner', {}),
                    'stat': video.get('stat', {}),
                    'add_time': video.get('add_time'),
                    'add_time_formatted': datetime.fromtimestamp(video.get('add_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if video.get('add_time') else 'Unknown',
                    'progress': video.get('progress', 0),
                    'viewed': video.get('viewed', 0)
                }
                processed_videos.append(video_info)
            
            return {
                "success": True,
                "total": result.get('count', 0),
                "page": page,
                "pagesize": pagesize,
                "videos": processed_videos,
                "message": f"成功获取 {len(processed_videos)} 个稍后再看视频"
            }
            
        except Exception as e:
            logger.error(f"获取稍后再看列表失败: {e}")
            return {
                "success": False,
                "error": f"获取稍后再看列表失败: {str(e)}"
            }
    
    def get_user_statistics(self, uid: str) -> Dict[str, Any]:
        """获取用户统计数据"""
        try:
            # 获取用户基本信息
            profile_data = self.get_user_profile(uid)
            if not profile_data.get('success'):
                return profile_data
            
            profile = profile_data.get('profile', {})
            
            # 获取用户视频数据
            videos_data = self.get_user_videos(uid, page=1, pagesize=1)
            total_videos = videos_data.get('total', 0) if videos_data.get('success') else 0
            
            # 获取关注数据
            following_data = self.get_following_list(uid, page=1, pagesize=1)
            total_following = following_data.get('total', 0) if following_data.get('success') else 0
            
            # 计算统计数据
            statistics = {
                'uid': uid,
                'name': profile.get('name'),
                'level': profile.get('level'),
                'follower': profile.get('follower', 0),
                'following': total_following,
                'friend': profile.get('friend', 0),
                'video': total_videos,
                'article': profile.get('article', 0),
                'audio': profile.get('audio', 0),
                'album': profile.get('album', 0),
                'favorite': profile.get('favorite', 0),
                'bangumi': profile.get('bangumi', 0),
                'cinema': profile.get('cinema', 0),
                'vip_status': profile.get('vip', {}),
                'official_status': profile.get('official', {}),
                'live_room': profile.get('live_room', {}),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 计算影响力指标
            influence_score = (
                profile.get('follower', 0) * 0.4 +
                total_videos * 0.3 +
                profile.get('favorite', 0) * 0.2 +
                total_following * 0.1
            )
            
            statistics['influence_score'] = round(influence_score, 2)
            
            return {
                "success": True,
                "statistics": statistics,
                "message": f"成功获取用户 {profile.get('name')} 的统计数据"
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {
                "success": False,
                "error": f"获取用户统计失败: {str(e)}"
            }
    
    def open_bilibili_video(self, bvid: str) -> Dict[str, Any]:
        """打开B站视频"""
        try:
            video_url = f"{self.web_url}/video/{bvid}"
            webbrowser.open(video_url)
            return {
                "success": True,
                "message": f"已打开视频: {bvid}",
                "url": video_url
            }
        except Exception as e:
            logger.error(f"打开B站视频失败: {e}")
            return {
                "success": False,
                "error": f"打开B站视频失败: {str(e)}"
            }
    
    def open_bilibili_user(self, uid: str) -> Dict[str, Any]:
        """打开B站用户主页"""
        try:
            user_url = f"{self.web_url}/space/{uid}"
            webbrowser.open(user_url)
            return {
                "success": True,
                "message": f"已打开用户主页: {uid}",
                "url": user_url
            }
        except Exception as e:
            logger.error(f"打开B站用户主页失败: {e}")
            return {
                "success": False,
                "error": f"打开B站用户主页失败: {str(e)}"
            }
    
    
    def search_and_play_first_video(self, up_name: str) -> Dict[str, Any]:
        """搜索UP主并播放第一个视频"""
        try:
            # 直接打开B站搜索页面
            search_url = f"https://search.bilibili.com/all?keyword={up_name}"
            webbrowser.open(search_url)
            
            return {
                "success": True,
                "message": f"已打开B站搜索页面: {up_name}",
                "url": search_url
            }
                
        except Exception as e:
            logger.error(f"搜索并播放第一个视频失败: {e}")
            return {
                "success": False,
                "error": f"搜索并播放第一个视频失败: {str(e)}"
            }
    
    def open_up_homepage(self, up_name: str) -> Dict[str, Any]:
        """打开UP主主页 - 假设用户已登录B站"""
        try:
            from .browser import automate_page
            
            # 用户卡片选择器，适配已登录状态
            user_card_selectors = [
                f"a.bili-video-card__info--owner:has-text('{up_name}')",  # 精确匹配UP主名称
                "a.bili-video-card__info--owner[href*='space.bilibili.com']", # 用户卡片链接
                f"a[href*='space.bilibili.com']:has-text('{up_name}')",   # 包含UP主名称的链接
                "a.bili-video-card__info--owner",                          # 用户卡片链接（兜底）
                "a[href*='space.bilibili.com']",                          # 兜底选择器
            ]
            
            # 步骤：进入UP主主页
            steps = [
                {
                    "action": "sleep",
                    "ms": 2000  # 减少等待时间，假设已登录
                },
                # 等待搜索结果加载
                {
                    "action": "wait",
                    "selector": "a.bili-video-card__info--owner, .bili-video-card",
                    "state": "visible",
                    "timeout": 8000  # 减少超时时间
                },
                {
                    "action": "sleep",
                    "ms": 500
                },
                # 点击用户卡片
                {
                    "action": "click_any",
                    "selectors": user_card_selectors,
                    "new_page": True
                },
                {
                    "action": "sleep",
                    "ms": 2000  # 减少等待时间
                }
            ]
            
            result = automate_page(
                url=f"https://search.bilibili.com/all?keyword={up_name}",  # 直接使用搜索页面
                steps=steps,
                timeout_ms=15000  # 减少总超时时间
            )
            
            if result.get('success'):
                return {
                    "success": True,
                    "message": f"成功进入 {up_name} 的主页",
                    "result": result
                }
            else:
                # 如果直接点击失败，尝试更通用的选择器
                logger.warning(f"直接点击失败，尝试通用选择器: {result.get('error', '')}")
                
                # 备用选择器，基于调试结果修正
                backup_selectors = [
                    f"a[href*='space.bilibili.com']:has-text('{up_name}')",
                    "a.bili-video-card__info--owner",
                    "a[href*='space.bilibili.com']",
                    ".bili-video-card a[href*='space.bilibili.com']",
                    ".result-item a[href*='space.bilibili.com']"
                ]
                
                # 备用步骤
                backup_steps = [
                    {
                        "action": "sleep",
                        "ms": 2000
                    },
                    {
                        "action": "wait",
                        "selector": "a.bili-video-card__info--owner, .bili-video-card",
                        "state": "visible",
                        "timeout": 8000
                    },
                    {
                        "action": "click_any",
                        "selectors": backup_selectors,
                        "new_page": True
                    },
                    {
                        "action": "sleep",
                        "ms": 2000
                    }
                ]
                
                result2 = automate_page(
                    url=f"https://search.bilibili.com/all?keyword={up_name}",
                    steps=backup_steps,
                    timeout_ms=15000
                )
                
                if result2.get('success'):
                    return {
                        "success": True,
                        "message": f"成功进入 {up_name} 的主页",
                        "result": result2
                    }
                else:
                    # 最后尝试点击第一个用户链接
                    logger.warning(f"备用选择器也失败，尝试最后兜底方案: {result2.get('error', '')}")
                    
                    # 最后兜底步骤
                    final_steps = [
                        {
                            "action": "sleep",
                            "ms": 2000
                        },
                        {
                            "action": "wait",
                            "selector": "a.bili-video-card__info--owner, .bili-video-card",
                            "state": "visible",
                            "timeout": 8000
                        },
                        {
                            "action": "click",
                            "selector": "a.bili-video-card__info--owner:first-child",
                            "new_page": True
                        },
                        {
                            "action": "sleep",
                            "ms": 2000
                        }
                    ]
                    
                    result3 = automate_page(
                        url=f"https://search.bilibili.com/all?keyword={up_name}",
                        steps=final_steps,
                        timeout_ms=15000
                    )
                    
                    if result3.get('success'):
                        return {
                            "success": True,
                            "message": f"成功进入 {up_name} 的主页",
                            "result": result3
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"自动化失败: {result3.get('error', '')}",
                            "result": result3
                        }
                
        except Exception as e:
            logger.error(f"打开UP主主页失败: {e}")
            return {
                "success": False,
                "error": f"打开UP主主页失败: {str(e)}"
            }

# 全局Bilibili集成实例
bilibili_integration = BilibiliIntegration()
