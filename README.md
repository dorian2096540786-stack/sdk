# 📚 课程表每日推送

自动查询 SeaTable 授课系统，每天 00:00 推送今日+明日课程到微信。

## 功能

- ✅ 自动查询南京大学 23临床 课程表
- ✅ 每天 00:00 定时执行
- ✅ 推送今日 + 明日课程到微信
- ✅ 无课程时温馨提醒
- ✅ 支持手动触发测试

## 配置步骤

### 1. 创建 GitHub 账号

访问 https://github.com 注册账号（如已有请跳过）

### 2. 创建新仓库

1. 点击右上角 **+** → **New repository**
2. 仓库名称填写：`course-reminder`
3. 选择 **Private**（私有仓库）
4. 点击 **Create repository**

### 3. 上传代码

有两种方式：

**方式 A：使用 GitHub 网页上传**
1. 在新建的仓库页面，点击 **uploading an existing file**
2. 将本文件夹中 `main.py`、`requirements.txt` 和 `.github/` 文件夹拖入
3. 点击 **Commit changes**

**方式 B：使用 Git 命令**
```bash
cd course-reminder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/course-reminder.git
git push -u origin main
```

### 4. 配置微信推送 (Server酱)

1. 访问 https://sct.ftqq.com/ 并登录（可用GitHub登录）
2. 获取你的 **SendKey**（形如 `SCTxxxxxxxx`）
3. 在 GitHub 仓库中依次点击：
   - **Settings** → **Secrets and variables** → **Actions**
   - 点击 **New repository secret**
   - Name: `SERVERCHAN_KEY`
   - Secret: 粘贴你的 SendKey

### 5. 测试运行

1. 在仓库页面点击 **Actions** 标签
2. 点击左侧 **Course Reminder**
3. 点击 **Run workflow** → **Run workflow**
4. 查看运行结果和微信推送

## 文件说明

```
course-reminder/
├── main.py                 # 主脚本
├── requirements.txt        # Python 依赖
├── .github/
│   └── workflows/
│       └── course_reminder.yml  # GitHub Actions 配置
└── README.md
```

## 自定义修改

如需修改查询条件（如学校、班级），请编辑 `main.py` 中的：

```python
await inputs[0].fill("南京大学")      # 修改学校
await inputs[1].fill("23临床")        # 修改班级
```

## 常见问题

**Q: 推送没收到？**
A: 检查 Server酱是否正确配置，查看 Actions 日志排查错误。

**Q: 想手动触发？**
A: 仓库 → Actions → Course Reminder → Run workflow

**Q: 想修改推送时间？**
A: 编辑 `.github/workflows/course_reminder.yml`，修改 cron 表达式。
