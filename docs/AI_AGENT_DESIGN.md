# AI Agent / Function Calling 设计

岗位加分项提到 LangChain 或 Function Calling。本项目不伪装成复杂 Agent 平台，而是用“任务型 Agent + 工具函数”的方式展示落地思路。

## Agent 角色设计

### 1. 异常分析 Agent

输入：异常描述、订单信息、库存信息。  
输出：异常类型、严重等级、责任部门、建议动作。

工具函数：

```text
classify_exception(text)
get_inventory(sku)
create_todo(owner, title, priority)
push_to_feishu(message)
```

### 2. 日报 Agent

输入：订单、库存、异常、待办、客户线索。  
输出：今日总结、重点风险、明日行动。

工具函数：

```text
get_dashboard()
build_daily_report()
push_to_feishu(report)
save_report(report)
```

### 3. 客服线索 Agent

输入：客户咨询内容。  
输出：客服回复、客户意向、需求摘要、跟进建议。

工具函数：

```text
answer_customer(message)
save_lead(name, contact, demand)
notify_sales(lead)
```

## Function Calling 预期输出格式

```json
{
  "exception_type": "库存不足 / 供应商延迟",
  "priority": "P1",
  "owner_department": "采购 / 仓储 / 供应商管理",
  "next_action": "优先确认可用库存和供应商补货交期，同时准备替代SKU方案。"
}
```

## 面试表达

> 我理解 Agent 不是一定要做得很重。这个岗位更重要的是能把 AI 接到业务流程里，所以我会先把任务拆成异常分析、日报总结、客服线索三个 Agent，再把每个 Agent 能调用的工具函数定义清楚，例如查库存、建待办、推送飞书、保存日报。这样比直接让大模型自由发挥更稳定，也更适合企业落地。
