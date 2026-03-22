# 🔄 AgentHub 自动检测系统使用指南

## 📅 检测频率

- **主检测**: 每 6 小时自动执行一次
- **日报**: 每天午夜生成
- **周报**: 每周一生成

---

## 🚀 系统组成

### 1. 自动检测脚本
**文件**: `scripts/auto_detect.py`

**功能**:
- ✅ Git 状态检测
- ✅ 代码质量检测
- ✅ 功能完整性检测
- ✅ 测试覆盖率检测
- ✅ 文档完整性检测
- ✅ GitHub 仓库检测
- ✅ 性能检测
- ✅ 安全检测
- ✅ 依赖检测
- ✅ Bug 检测

**自动完善**:
- 📝 创建缺失文档
- 🔧 修复代码质量问题
- 📊 更新优先级文档
- 🤖 推送改进到 GitHub

### 2. 运行脚本
**文件**: `scripts/run_detection.sh`

**功能**:
- 🔄 执行自动检测
- 📝 记录日志
- ✅ 检查执行结果

### 3. Cron 配置
**文件**: `scripts/crontab.txt`

**定时任务**:
```bash
# 每6小时执行一次
0 */6 * * * cd /workspace/projects/workspace/AgentHub && bash scripts/run_detection.sh

# 每天午夜生成日报
0 0 * * * cd /workspace/projects/workspace/AgentHub && python3 scripts/auto_detect.py

# 每周一生成周报
0 0 * * 1 cd /workspace/projects/workspace/AgentHub && python3 scripts/generate_weekly_report.py
```

### 4. 仪表板
**文件**: `scripts/dashboard.py`

**功能**:
- 📊 实时显示检测状态
- 📈 显示最近7天趋势
- 💡 给出改进建议

### 5. 周报生成
**文件**: `scripts/generate_weekly_report.py`

**功能**:
- 📊 统计本周检测数据
- 📈 分析趋势
- 🎯 设定下周目标

---

## 🎯 检测指标

### 指标清单

| 指标 | 权重 | 目标分数 | 当前分数 |
|------|------|---------|---------|
| Git 状态 | 10% | 100 | 80 |
| 代码质量 | 15% | 100 | 100 |
| 功能完整性 | 20% | 100 | 100 |
| 测试覆盖率 | 15% | 80 | 60 |
| 文档完整性 | 10% | 100 | 100 |
| GitHub 状态 | 10% | 100 | 100 |
| 性能 | 5% | 100 | 100 |
| 安全 | 5% | 100 | 100 |
| 依赖 | 5% | 100 | 50 |
| Bug 数量 | 5% | 0 | 3 |

### 评分标准

- **90-100**: ✅ 优秀
- **80-89**: ⚠️ 良好
- **70-79**: ⚠️ 一般
- **0-69**: ❌ 需要改进

---

## 📊 检测报告

### 报告位置
```
/workspace/projects/workspace/AgentHub/reports/detection_report_YYYYMMDD_HHMMSS.json
```

### 报告格式
```json
{
  "timestamp": "2026-03-23 02:52:03",
  "status": "completed",
  "checks": {
    "git": {"score": 80, ...},
    "code_quality": {"score": 100, ...},
    ...
  },
  "overall_score": 87.5,
  "improvements": {
    "files_changed": 1,
    "actions": ["Updated PRIORITY.md"]
  }
}
```

---

## 🚀 使用方法

### 手动执行检测
```bash
cd /workspace/projects/workspace/AgentHub
python3 scripts/auto_detect.py
```

### 查看仪表板
```bash
cd /workspace/projects/workspace/AgentHub
python3 scripts/dashboard.py
```

### 生成周报
```bash
cd /workspace/projects/workspace/AgentHub
python3 scripts/generate_weekly_report.py
```

### 查看日志
```bash
cd /workspace/projects/workspace/AgentHub
tail -f logs/detection.log
```

---

## ⚙️ 配置

### 修改检测频率
编辑 `scripts/crontab.txt`:

```bash
# 改为每3小时执行一次
0 */3 * * * cd /workspace/projects/workspace/AgentHub && bash scripts/run_detection.sh

# 改为每小时执行一次
0 * * * * cd /workspace/projects/workspace/AgentHub && bash scripts/run_detection.sh
```

然后重新加载 cron:
```bash
crontab scripts/crontab.txt
```

### 修改检测项
编辑 `scripts/auto_detect.py` 的 `run_detection()` 方法，添加或删除检测项。

---

## 🔍 检测详情

### 1. Git 状态检测
- 检查是否有未提交的更改
- 检查最近的提交记录
- 检查分支状态

### 2. 代码质量检测
- Python 语法检查
- 导入错误检测
- 代码风格检查

### 3. 功能完整性检测
- 检查核心文件是否存在
- 统计功能完成度
- 计算完成率

### 4. 测试覆盖率检测
- 统计测试文件数量
- 运行测试套件
- 计算覆盖率

### 5. 文档完整性检测
- 检查必需文档是否存在
- 统计文档完成度

### 6. GitHub 仓库检测
- 检查远程仓库连接
- 检查最新提交
- 检查推送状态

### 7. 性能检测
- 测量导入时间
- 检测性能瓶颈

### 8. 安全检测
- 检测硬编码密钥
- 检测敏感数据
- 检测安全漏洞

### 9. 依赖检测
- 检查 requirements.txt
- 检测依赖版本
- 检测依赖冲突

### 10. Bug 检测
- 检测 TODO 注释
- 检测 FIXME 注释
- 检测 BUG 注释

---

## 📈 改进措施

### 自动改进
- 📝 创建缺失的文档
- 🔧 修复代码质量问题
- 📊 更新优先级文档
- 🤖 推送改进到 GitHub

### 手动改进
根据检测报告中的建议，手动进行改进：
- 增加单元测试
- 修复 Bug
- 优化性能
- 完善文档

---

## 🎯 目标

### 短期目标（本周）
- [ ] 提高测试覆盖率至 80%
- [ ] 修复所有 Bug
- [ ] 添加 requirements.txt
- [ ] Git 状态保持 clean

### 中期目标（本月）
- [ ] 总体分数达到 90/100
- [ ] 完成所有待开发功能
- [ ] 建立完整的 CI/CD
- [ ] 实现自动化部署

### 长期目标（季度）
- [ ] 总体分数达到 95/100
- [ ] 测试覆盖率达到 90%
- [ ] 建立完整的监控体系
- [ ] 实现自动化运维

---

## 📞 支持

如有问题，请查看：
- 📄 检测日志: `logs/detection.log`
- 📊 检测报告: `reports/detection_report_*.json`
- 💡 建议反馈: GitHub Issues

---

## 📅 下次检测

⏰ **时间**: 6小时后
🔄 **状态**: 自动运行中
📊 **预计完成**: 2026-03-23 08:52:03

---

**系统状态**: ✅ 运行中
**优先级**: P1 - 最高优先级
**版本**: v0.6.0-alpha
