# B站视频播放操作流程详解

## 🎯 优化后的操作流程

针对B站视频播放，我们实现了以下标准操作流程：

### 📋 完整操作步骤

```
1. 打开B站首页 (https://www.bilibili.com)
   ↓
2. 等待页面加载 (2秒)
   ↓
3. 关闭可能的弹窗 (可选操作)
   ↓
4. 点击搜索框
   ↓
5. 清空搜索框并输入关键词
   ↓
6. 按回车键进行搜索
   ↓
7. 等待搜索结果加载
   ↓
8. 使用光标点击第一个视频链接
   ↓
9. 等待视频页面加载
   ↓
10. 使用光标点击播放按钮
```

### 🔧 技术实现细节

#### **1. 搜索框操作**
```python
# 搜索框选择器（按优先级排序）
search_selectors = [
    "input#nav-searchform input",      # B站导航搜索框
    "input[type=search]",              # 标准搜索框
    ".nav-search-input input",         # 导航搜索输入框
]

# 操作步骤
{"action": "click", "selector": "input#nav-searchform input, input[type=search], .nav-search-input input"},
{"action": "type", "selector": "input#nav-searchform input, input[type=search], .nav-search-input input", 
 "text": keyword, "clear": True},
{"action": "press", "selector": "input#nav-searchform input, input[type=search], .nav-search-input input", "key": "Enter"},
```

#### **2. 视频链接点击**
```python
# 视频链接选择器
video_link_selectors = [
    "a[href*='/video/']:first-of-type",     # B站视频链接
    ".video-item a:first-of-type",          # 视频项目链接
    ".bili-video-card a:first-of-type",     # B站视频卡片链接
]

# 操作步骤
{"action": "click", "selector": "a[href*='/video/']:first-of-type, .video-item a:first-of-type, .bili-video-card a:first-of-type"},
```

#### **3. 光标点击播放按钮**
```python
def click_with_mouse_on_locator(locator):
    """真实鼠标点击操作，模拟人类行为"""
    # 1. 滚动到元素可见
    locator.scroll_into_view_if_needed(timeout=2000)
    
    # 2. 获取元素位置
    box = locator.bounding_box()
    if not box:
        return False
    
    # 3. 计算点击坐标（元素中心）
    x = box['x'] + box['width'] / 2
    y = box['y'] + box['height'] / 2
    
    # 4. 模拟真实鼠标行为
    page.mouse.move(x, y)           # 移动到目标位置
    page.wait_for_timeout(200)      # 短暂停留，模拟人类反应
    page.mouse.click(x, y)          # 单击
    page.wait_for_timeout(300)      # 等待响应
    
    return True
```

#### **4. B站专用播放按钮选择器**
```python
bilibili_play_selectors = [
    '.bpx-player-ctrl-play',                    # B站主播放按钮
    '.bpx-player-ctrl-play-icon',               # B站播放图标
    '.bpx-player-ctrl-play-btn',                # B站播放按钮
    '.bpx-player-sending-area',                 # B站播放区域
    '.bpx-player-ctrl-play-icon-wrapper',       # B站播放图标包装器
    '.bpx-player-ctrl-play-icon-container',     # B站播放图标容器
    '.play-button',                             # 通用播放按钮
    '.play-btn',                                # 通用播放按钮
    'button[title*="播放"]',                    # 带播放文字的按钮
    'button[aria-label*="播放"]',               # 无障碍标签
    "[class*='play'][class*='btn']",            # 包含play和btn的类名
    "[class*='play'][class*='icon']",           # 包含play和icon的类名
]
```

### 🎮 多策略播放机制

#### **策略1: 主页面播放按钮点击**
```python
# 尝试在主页面点击播放按钮
for selector in bilibili_play_selectors:
    locator = page.locator(selector).first
    if locator.is_visible(timeout=1500):
        if click_with_mouse_on_locator(locator):
            log(f"光标点击播放按钮成功: {selector}")
            return True
```

#### **策略2: iframe内播放按钮点击**
```python
# 尝试在iframe内点击播放按钮
for frame in page.frames:
    for selector in bilibili_play_selectors:
        locator = frame.locator(selector).first
        if locator.is_visible(timeout=1500):
            if click_with_mouse_on_locator(locator):
                log(f"在iframe内光标点击播放按钮成功: {selector}")
                return True
```

#### **策略3: 播放器容器中心点击**
```python
# 退而求其次：点击播放器容器中心
container_selectors = [
    '.bpx-player-container',                # B站播放器容器
    '.bilibili-player',                     # B站播放器
    '.video-player',                        # 通用视频播放器
    "[class*='player']",                    # 包含player的类名
    "[class*='video']"                      # 包含video的类名
]

for selector in container_selectors:
    locator = page.locator(selector).first
    if locator.is_visible(timeout=1500):
        if click_with_mouse_on_locator(locator):
            log(f"光标点击播放器容器成功: {selector}")
            return True
```

### ⏱️ 时间控制优化

```python
# 智能延迟控制
delays = {
    'page_load': 2000,          # 页面加载等待
    'popup_close': 500,          # 弹窗关闭等待
    'search_click': 300,         # 搜索框点击等待
    'search_type': 500,          # 搜索输入等待
    'search_submit': 2000,       # 搜索提交等待
    'results_load': 1000,        # 搜索结果加载等待
    'video_click': 3000,         # 视频点击等待
    'video_page_load': 2000,     # 视频页面加载等待
    'play_click': 2000,          # 播放点击等待
    'mouse_move': 200,           # 鼠标移动等待
    'mouse_click': 300,          # 鼠标点击等待
}
```

### 🔍 错误处理和日志

#### **详细日志记录**
```python
def log_operation(operation: str, details: str):
    """记录操作日志"""
    log_entry = {
        "timestamp": time.time(),
        "operation": operation,
        "details": details,
        "success": "成功" in details
    }
    logger.info(f"B站操作: {operation} - {details}")
```

#### **错误恢复机制**
```python
def retry_bilibili_operation(operation_func, max_retries: int = 3):
    """B站操作重试机制"""
    for attempt in range(max_retries):
        try:
            result = operation_func()
            if result:
                return result
        except Exception as e:
            logger.warning(f"B站操作失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # 重试前等待
    
    return False
```

### 📊 使用示例

#### **基本使用**
```python
# 使用优化后的B站搜索播放功能
result = automate_bilibili_search_and_play("Python教程")

# 返回结果
{
    "success": True,
    "title": "视频页面标题",
    "current_url": "https://www.bilibili.com/video/BV1234567890",
    "logs": [
        "等待页面加载",
        "点击搜索框",
        "输入关键词: Python教程",
        "按回车搜索",
        "等待搜索结果加载",
        "光标点击第一个视频链接",
        "等待视频页面加载",
        "光标点击播放按钮成功: .bpx-player-ctrl-play",
        "光标点击播放流程完成"
    ]
}
```

#### **自然语言调用**
```python
# 通过自然语言调用
instruction = "在B站搜索Python教程并播放第一个视频"
steps = parse_natural_language_instruction(instruction)
result = execute_natural_language_instruction(instruction)
```

### 🎯 核心优势

1. **真实光标操作**: 使用真实鼠标移动和点击，模拟人类行为
2. **多策略容错**: 主页面、iframe、容器中心多种点击策略
3. **B站专用优化**: 针对B站页面结构优化的选择器
4. **智能时间控制**: 根据操作类型智能调整等待时间
5. **详细日志记录**: 完整的操作过程记录，便于调试
6. **错误恢复机制**: 自动重试和降级策略

### 🔧 配置选项

```python
# 在 config.py 中可以配置
class Settings(BaseSettings):
    # B站专用配置
    bilibili_search_timeout: int = 10000      # 搜索超时时间
    bilibili_play_timeout: int = 15000        # 播放超时时间
    bilibili_mouse_delay: int = 200           # 鼠标操作延迟
    bilibili_retry_count: int = 3             # 重试次数
```

这套优化后的B站操作流程确保了：
- ✅ 严格按照"搜索框搜索 → 光标点击视频 → 光标点击播放"的流程
- ✅ 使用真实鼠标操作，模拟人类行为
- ✅ 多策略容错，提高成功率
- ✅ 详细的日志记录，便于调试和监控









