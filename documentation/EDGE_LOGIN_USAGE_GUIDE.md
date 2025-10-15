# Edge浏览器登录功能使用指南

## 快速开始

### 1. 启动系统

```bash
# 启动图形界面
python main.py

# 或使用命令行模式
python main.py --cli "打开淘宝"
```

### 2. 添加网站凭据

1. 启动图形界面后，点击侧边栏的"凭据管理"
2. 点击"添加凭据"
3. 填写网站信息：
   - 网站名称：如"淘宝"
   - 网站URL：如"https://www.taobao.com"
   - 用户名/账号
   - 密码
4. 保存凭据

### 3. 测试自动登录

```bash
# 测试淘宝自动登录
python main.py --cli "打开淘宝"

# 测试京东自动登录
python main.py --cli "打开京东"

# 测试B站自动登录
python main.py --cli "打开B站"
```

## 支持的网站

### 已配置专用选择器的网站

1. **淘宝** (taobao.com)
   - 登录页面：https://login.taobao.com
   - 支持自动登录检测

2. **天猫** (tmall.com)
   - 登录页面：https://login.tmall.com
   - 支持自动登录检测

3. **京东** (jd.com)
   - 登录页面：https://passport.jd.com/new/login.aspx
   - 支持自动登录检测

4. **哔哩哔哩** (bilibili.com)
   - 登录页面：https://passport.bilibili.com/login
   - 支持自动登录检测

5. **微博** (weibo.com)
   - 登录页面：https://passport.weibo.cn/signin/login
   - 支持自动登录检测

6. **知乎** (zhihu.com)
   - 登录页面：https://www.zhihu.com/signin
   - 支持自动登录检测

### 通用支持

所有使用标准HTML登录表单的网站都支持：
- 用户名/邮箱/手机号登录
- 密码登录
- 智能检测验证码需求

## 功能特性

### ✅ 已验证功能

1. **Edge浏览器支持**
   - 完全支持Microsoft Edge浏览器
   - 自动启动和配置
   - 安全参数设置

2. **登录状态检测**
   - 智能识别登录页面
   - 检测登录需求
   - 支持多种检测方式

3. **凭据管理**
   - 安全存储网站凭据
   - 智能匹配网站和凭据
   - 支持多账号管理

4. **浏览器自动化**
   - 自动填写登录表单
   - 智能等待页面加载
   - 错误处理和重试

### ⚠️ 注意事项

1. **选择器更新**
   - 部分网站页面结构可能变化
   - 需要定期更新选择器配置
   - 系统会自动尝试通用选择器

2. **验证码处理**
   - 检测到验证码时会暂停自动登录
   - 需要手动输入验证码
   - 支持常见验证码类型

3. **网络环境**
   - 需要稳定的网络连接
   - 支持代理配置
   - 自动处理超时和重试

## 故障排除

### 常见问题

1. **Edge浏览器无法启动**
   ```bash
   # 检查Edge浏览器是否已安装
   # 确保Playwright已正确安装
   pip install playwright
   playwright install chromium
   ```

2. **登录失败**
   - 检查凭据是否正确
   - 确认网站URL是否正确
   - 检查网络连接

3. **选择器错误**
   - 网站页面结构可能已变化
   - 尝试手动登录一次
   - 联系技术支持更新选择器

### 调试模式

```bash
# 启用详细日志
python main.py --verbose --cli "打开淘宝"

# 运行测试脚本
python test_edge_login_sync.py
```

## 高级配置

### 浏览器参数配置

编辑 `src/tools/browser_config_safe.py`：

```python
def get_safe_browser_args() -> List[str]:
    return [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        # 添加自定义参数
    ]
```

### 网站选择器配置

编辑 `src/tools/auto_login.py`：

```python
self.site_specific_configs = {
    'example.com': {
        'username_selector': '#username',
        'password_selector': '#password',
        'login_button_selector': '#login-btn',
        'need_captcha': False
    }
}
```

## 安全建议

1. **凭据安全**
   - 定期更换密码
   - 使用强密码
   - 不要在公共设备上保存凭据

2. **网络安全**
   - 使用HTTPS连接
   - 避免在公共WiFi上使用
   - 定期检查登录记录

3. **系统安全**
   - 定期更新系统
   - 使用防病毒软件
   - 限制系统访问权限

## 技术支持

### 日志文件

- 应用日志：`logs/app.log`
- 错误日志：控制台输出

### 测试脚本

- 完整测试：`test_edge_login_integration.py`
- 同步测试：`test_edge_login_sync.py`
- 验证脚本：`edge_login_verification.py`

### 联系方式

如遇到问题，请提供：
1. 错误日志
2. 操作步骤
3. 系统环境信息
4. 网络环境描述

---

**祝您使用愉快！** 🎉

