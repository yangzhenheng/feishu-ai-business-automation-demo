# GitHub 上传命令

## 1. 初始化本地仓库

```bash
cd feishu-ai-business-automation-demo
git init
git add .
git commit -m "init: AI business automation demo"
```

## 2. 在 GitHub 创建仓库

仓库名建议：

```text
feishu-ai-business-automation-demo
```

仓库描述建议：

```text
AI + Feishu low-code + WeCom/Feishu bot + AI customer service + supply chain workflow automation demo.
```

## 3. 绑定远程仓库并推送

把下面的地址换成你自己的 GitHub 仓库地址：

```bash
git branch -M main
git remote add origin https://github.com/YOUR_NAME/feishu-ai-business-automation-demo.git
git push -u origin main
```

## 4. README 重点展示

GitHub 首页 README 要让 HR 和面试官一眼看到：

1. 项目解决什么业务问题。
2. 为什么和 AI + 飞书低代码岗位相关。
3. 如何启动。
4. 有哪些接口和演示功能。
5. 可扩展到真实业务的方向。

## 5. 后续可以补截图

建议后续补充：

```text
docs/images/dashboard.png
docs/images/daily-report.png
docs/images/bot-command.png
docs/images/customer-service.png
```

然后在 README 顶部加上截图，面试官感知会更强。
