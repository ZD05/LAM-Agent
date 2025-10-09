"""
自然语言指令解析器
将复杂的自然语言指令拆分成有序的操作步骤
"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OperationStep:
    """操作步骤"""
    action: str  # 操作类型
    target: str  # 目标对象
    query: str   # 搜索关键词
    order: int   # 执行顺序
    description: str  # 步骤描述


class NaturalLanguageParser:
    """自然语言指令解析器"""
    
    def __init__(self):
        self.instruction = ""  # 存储原始指令
        self.last_explicit_site: Optional[str] = None  # 最近一次明确站点
        # 操作关键词映射
        self.action_keywords = {
            "打开": "open",
            "搜索": "search", 
            "查找": "search",
            "播放": "play",
            "点击": "click",
            "进入": "enter",
            "浏览": "browse",
            "查看": "view"
        }
        
        # 网站关键词映射
        self.site_keywords = {
            "b站": "bilibili.com",
            "bilibili": "bilibili.com",
            "youtube": "youtube.com",
            "淘宝": "taobao.com",
            "京东": "jd.com",
            "百度": "baidu.com",
            "谷歌": "bing.com"
        }
        
        # 分隔符
        self.separators = ["，", ",", "然后", "接着", "再", "最后"]
    
    def parse_instruction(self, instruction: str) -> List[OperationStep]:
        """
        解析自然语言指令
        
        Args:
            instruction: 自然语言指令
            
        Returns:
            操作步骤列表
        """
        self.instruction = instruction  # 存储原始指令
        logger.info(f"开始解析指令: {instruction}")
        
        # 预处理：清理指令
        instruction = self._preprocess_instruction(instruction)
        
        # 拆分指令
        steps_text = self._split_instruction(instruction)
        
        # 解析每个步骤（支持上下文继承最近一次明确站点）
        operations = []
        for i, step_text in enumerate(steps_text):
            operation = self._parse_step(step_text.strip(), i + 1)
            if operation:
                # 若本步明确了站点，则刷新上下文
                if operation.target and operation.target != "browser":
                    self.last_explicit_site = operation.target
                operations.append(operation)
        
        logger.info(f"解析完成，共{len(operations)}个操作步骤")
        return operations
    
    def _preprocess_instruction(self, instruction: str) -> str:
        """预处理指令"""
        # 移除多余空格
        instruction = re.sub(r'\s+', ' ', instruction.strip())
        
        # 标准化分隔符
        for sep in self.separators:
            instruction = instruction.replace(sep, '，')
        
        return instruction
    
    def _split_instruction(self, instruction: str) -> List[str]:
        """拆分指令为多个步骤"""
        # 按分隔符拆分
        steps = re.split(r'[，,]', instruction)
        
        # 清理空步骤
        steps = [step.strip() for step in steps if step.strip()]
        
        return steps
    
    def _parse_step(self, step_text: str, order: int) -> Optional[OperationStep]:
        """解析单个步骤"""
        logger.debug(f"解析步骤: {step_text}")
        
        # 识别操作类型
        action = self._extract_action(step_text)
        if not action:
            logger.warning(f"无法识别操作类型: {step_text}")
            return None
        
        # 识别目标对象
        target = self._extract_target(step_text)
        
        # 识别搜索关键词
        query = self._extract_query(step_text)
        
        # 生成步骤描述
        description = self._generate_description(action, target, query)
        
        # 上下文继承：若省略站点且属于搜索/播放/查看类操作，继承最近一次明确站点
        if (
            (not target or target == "browser") and
            action in {"search", "play", "view", "browse", "enter", "click"} and
            self.last_explicit_site
        ):
            target = self.last_explicit_site

        operation = OperationStep(
            action=action,
            target=target,
            query=query,
            order=order,
            description=description
        )
        
        logger.debug(f"解析结果: {operation}")
        return operation
    
    def _extract_action(self, step_text: str) -> Optional[str]:
        """提取操作类型"""
        step_lower = step_text.lower()
        
        for keyword, action in self.action_keywords.items():
            if keyword in step_text:
                return action
        
        return None
    
    def _extract_target(self, step_text: str) -> str:
        """提取目标对象"""
        step_lower = step_text.lower()
        
        # 检查是否包含网站关键词
        for keyword, site in self.site_keywords.items():
            if keyword in step_text:
                return site
        
        # 如果没有明确的网站，检查上下文
        # 如果当前步骤是搜索或播放，且前面有打开B站等操作，则使用B站
        if any(k in step_text for k in ["搜索", "播放", "查看"]) and self._has_bilibili_context():
            return "bilibili.com"
        
        # 如果没有明确的网站，返回通用目标
        return "browser"
    
    def _extract_query(self, step_text: str) -> str:
        """提取搜索关键词"""
        # 更保守的清洗：仅移除前缀动词与站点词，不清理内容关键词
        text = step_text
        # 去除动作词（仅去前缀位置的匹配）
        for keyword in self.action_keywords.keys():
            if text.startswith(keyword):
                text = text[len(keyword):].strip()
        # 若包含“在XX中/在XX里/到XX/进入XX”等前置短语，去掉该短语
        text = re.sub(r'^在.+?(中|里)\s*', '', text)
        text = re.sub(r'^(到|进入)\s*.+?\s*', '', text)
        # 去除站点词（出现于开头或以“在XX”短语中时）
        for keyword in self.site_keywords.keys():
            text = re.sub(rf'^({keyword})', '', text)
            text = text.replace(keyword, '').strip()
        # 轻量修饰词移除
        for modifier in ["第一个", "第1个", "主页", "首页"]:
            text = text.replace(modifier, '').strip()
        # 去除结尾标点
        text = re.sub(r'[，,。！？]+$', '', text).strip()
        return text or step_text
    
    def _has_bilibili_context(self) -> bool:
        """检查是否有B站上下文"""
        # 检查原始指令中是否包含B站相关关键词
        return any(k in self.instruction for k in ["B站", "bilibili", "哔哩哔哩"])
    
    def _generate_description(self, action: str, target: str, query: str) -> str:
        """生成步骤描述"""
        action_map = {
            "open": "打开",
            "search": "搜索", 
            "play": "播放",
            "click": "点击",
            "enter": "进入",
            "browse": "浏览",
            "view": "查看"
        }
        
        action_desc = action_map.get(action, action)
        
        if target == "browser":
            return f"{action_desc}: {query}"
        else:
            return f"在{target}中{action_desc}: {query}"


def parse_natural_language_instruction(instruction: str) -> List[OperationStep]:
    """
    解析自然语言指令的便捷函数
    
    Args:
        instruction: 自然语言指令
        
    Returns:
        操作步骤列表
    """
    parser = NaturalLanguageParser()
    return parser.parse_instruction(instruction)
