async function getJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { Accept: 'application/json', ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(`状态码 ${response.status}: ${message || response.statusText}`);
  }
  return response.json();
}

function el(id) {
  return document.getElementById(id);
}

function safe(value) {
  return value === null || value === undefined || value === '' ? '未填写' : value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function showError(targetId, error) {
  const target = el(targetId);
  if (target) {
    target.textContent = `接口调用失败：${error.message || error}`;
  }
}

function renderBusinessCard(data, detailHtml = '') {
  return `
    <div class="business-card">
      <div class="business-card-head">
        <span>${escapeHtml(data.module || '业务模块')}</span>
        <strong>${escapeHtml(data.core_result || '已完成接口调用')}</strong>
      </div>
      ${detailHtml}
      <div class="risk-line"><b>风险点：</b>${escapeHtml(data.risk || '暂无明显风险')}</div>
      <div class="next-line"><b>下一步：</b>${escapeHtml(data.next_action || '等待下一步处理')}</div>
    </div>
  `;
}

function renderFeishuPushStatus(data) {
  const detail = data.feishu_push_detail || {};
  const rawStatus = detail.status || data.feishu_push || 'skipped';
  const normalizedStatus = rawStatus === 'success' ? 'success' : rawStatus.startsWith('failed') ? 'failed' : rawStatus;
  const title = detail.title || (normalizedStatus === 'success' ? '推送成功' : normalizedStatus === 'failed' ? '推送失败' : '推送跳过');
  const reason = detail.reason || (normalizedStatus === 'success' ? 'Webhook 已返回成功响应' : data.feishu_push || '未配置飞书 Webhook');
  const nextAction = detail.next_action || (normalizedStatus === 'success' ? '负责人可在群内继续跟进异常单和财务复核' : '检查 .env 中的 FEISHU_WEBHOOK_URL 配置');
  const messageSummary = detail.message_summary || (data.ai_report || '').split('。')[0] + '。';

  return `
    <div class="push-card ${escapeHtml(normalizedStatus)}">
      <div class="push-card-head">
        <span class="status-badge ${escapeHtml(normalizedStatus)}">${escapeHtml(title)}</span>
        <strong>平台：${escapeHtml(detail.platform || '飞书机器人')}</strong>
      </div>
      <div class="push-field"><b>群聊：</b>${escapeHtml(detail.group || 'AI业务自动化Demo测试群')}</div>
      <div class="push-field"><b>时间：</b>${escapeHtml(detail.time || new Date().toLocaleString('zh-CN', { hour12: false }))}</div>
      <div class="push-field"><b>消息摘要：</b>${escapeHtml(messageSummary)}</div>
      <div class="push-field"><b>原因：</b>${escapeHtml(reason)}</div>
      <div class="push-field"><b>下一步建议：</b>${escapeHtml(nextAction)}</div>
    </div>
  `;
}

async function loadDashboard() {
  try {
    const data = await getJson('/api/dashboard');
    const m = data.metrics;
    el('metrics').innerHTML = `
      <div class="metric"><span>订单总数</span><strong>${m.orders}</strong><small>Orders</small></div>
      <div class="metric danger"><span>未关闭异常</span><strong>${m.active_exceptions}</strong><small>Exceptions</small></div>
      <div class="metric warning"><span>库存预警</span><strong>${m.low_stock}</strong><small>Low Stock</small></div>
      <div class="metric"><span>未完成待办</span><strong>${m.open_todos}</strong><small>Todos</small></div>
      <div class="metric"><span>客户线索</span><strong>${m.open_leads}</strong><small>Leads</small></div>
    `;

    el('exceptions').innerHTML = data.exceptions.map(item => `
      <div class="item">
        <strong>${escapeHtml(item.exception_no)} | ${escapeHtml(item.exception_type)} | ${escapeHtml(item.priority)}</strong>
        <small>${escapeHtml(item.order_no)} | 负责人：${escapeHtml(item.owner)} | 状态：${escapeHtml(item.status)}<br>${escapeHtml(item.reason)}</small>
      </div>
    `).join('') || '<p>暂无异常</p>';

    el('low-stock').innerHTML = data.low_stock.map(item => `
      <div class="item">
        <strong>${escapeHtml(item.sku)} | ${escapeHtml(item.product_name)}</strong>
        <small>当前库存：${item.current_stock} | 安全库存：${item.safety_stock} | 缺口：${item.safety_stock - item.current_stock} | 供应商：${escapeHtml(item.supplier)} | 仓库：${escapeHtml(item.warehouse)}</small>
      </div>
    `).join('') || '<p>暂无库存预警</p>';

    el('leads').innerHTML = data.leads.map(item => `
      <div class="item">
        <strong>${escapeHtml(item.name)} | ${escapeHtml(item.intent_level)}意向</strong>
        <small>${escapeHtml(item.demand)}<br>联系方式：${escapeHtml(safe(item.contact))} | 来源：${escapeHtml(item.source)} | 状态：${escapeHtml(item.status)}</small>
      </div>
    `).join('') || '<p>暂无客户线索</p>';
  } catch (error) {
    alert(`Dashboard 加载失败：${error.message}`);
  }
}

async function loadEcommerceFlow() {
  const flowTarget = el('ecommerce-flow');
  const valueTarget = el('ecommerce-values');
  if (!flowTarget || !valueTarget) return;
  flowTarget.innerHTML = '<div class="flow-step"><strong>正在加载业务闭环...</strong></div>';
  valueTarget.innerHTML = '';

  try {
    const data = await getJson('/api/ecommerce/flow');
    flowTarget.innerHTML = data.flow.map((step, index) => `
      <div class="flow-step">
        <span>${String(index + 1).padStart(2, '0')}</span>
        <strong>${escapeHtml(step)}</strong>
        <small>${escapeHtml(data.scene)}</small>
      </div>
    `).join('');
    valueTarget.innerHTML = `<div class="value-card">${escapeHtml(data.business_value)}</div>`;
  } catch (error) {
    flowTarget.innerHTML = `<div class="flow-step error">接口调用失败：${escapeHtml(error.message)}</div>`;
  }
}

async function runFullFlow() {
  el('full-flow-status').textContent = '正在执行完整业务闭环...';
  el('full-flow-steps').innerHTML = '';
  el('full-flow-report').textContent = '正在生成 AI 日报...';
  el('feishu-push-status').innerHTML = '<div class="push-card pending">正在检查飞书推送...</div>';
  el('business-values').innerHTML = '';

  try {
    const data = await getJson('/api/demo/run-full-flow', { method: 'POST' });
    el('full-flow-status').textContent = `${data.title} | ${data.scene}`;
    el('full-flow-steps').innerHTML = data.steps.map(step => `
      <div class="workflow-step ${step.status}">
        <span>Step ${step.step}</span>
        <strong>${escapeHtml(step.name)}</strong>
        <small>${escapeHtml(step.summary)}</small>
      </div>
    `).join('');
    el('full-flow-report').textContent = data.ai_report;
    el('feishu-push-status').innerHTML = renderFeishuPushStatus(data);
    el('business-values').innerHTML = data.business_value.map(value => `
      <div class="value-card">${escapeHtml(value)}</div>
    `).join('');
    await loadWorkflowLogs();
  } catch (error) {
    el('full-flow-status').textContent = `接口调用失败：${error.message}`;
    el('full-flow-report').textContent = 'AI 日报生成失败。';
    el('feishu-push-status').innerHTML = `
      <div class="push-card failed">
        <span class="status-badge failed">推送失败</span>
        <div class="push-field"><b>原因：</b>${escapeHtml(error.message)}</div>
        <div class="push-field"><b>下一步建议：</b>检查 /api/demo/run-full-flow 接口和服务日志。</div>
      </div>
    `;
  }
}

async function runMockApi(type) {
  const routes = {
    sync: ['/api/mock/shop/orders/sync', 'POST'],
    inventory: ['/api/mock/wms/inventory/check', 'POST'],
    logistics: ['/api/mock/logistics/track', 'POST'],
    finance: ['/api/mock/finance/reconcile', 'POST'],
    crm: ['/api/mock/crm/leads', 'POST']
  };
  const route = routes[type];
  if (!route) {
    el('mock-api-result').textContent = '接口调用失败：未知按钮类型';
    return;
  }

  const [url, method] = route;
  el('mock-api-result').textContent = '正在调用模拟 API...';
  try {
    const data = await getJson(url, { method });
    let detailHtml = '';
    if (type === 'inventory') {
      detailHtml = `<div class="mini-grid">${data.low_stock.map(item => `
        <div><b>${escapeHtml(item.sku)}</b><br>${escapeHtml(item.product)}<br>当前 ${item.stock} / 安全 ${item.safe_stock} / 缺口 ${item.gap}</div>
      `).join('')}</div>`;
    }
    if (type === 'finance') {
      detailHtml = `<div class="numbers"><span>订单金额 ${data.order_amount}</span><span>已回款 ${data.received_amount}</span><span>差异 ${data.difference}</span></div>`;
    }
    if (type === 'crm') {
      detailHtml = `<div class="mini-grid">${data.leads.map(item => `
        <div><b>${escapeHtml(item.name)}</b><br>来源：${escapeHtml(item.source)}<br>意向：${escapeHtml(item.intent)} | ${escapeHtml(item.status)}</div>
      `).join('')}</div>`;
    }
    if (type === 'sync') {
      detailHtml = `<div class="numbers"><span>同步 ${data.synced_count}</span><span>异常 ${data.exception_count}</span></div>`;
    }
    if (type === 'logistics') {
      detailHtml = `<div class="numbers"><span>运单 ${escapeHtml(data.tracking_no)}</span><span>状态 ${escapeHtml(data.status)}</span><span>${escapeHtml(data.reason)}</span></div>`;
    }
    el('mock-api-result').innerHTML = renderBusinessCard(data, detailHtml);
  } catch (error) {
    showError('mock-api-result', error);
  }
}

async function loadWorkflowLogs() {
  const target = el('workflow-logs');
  target.innerHTML = '<div class="item">正在加载执行日志...</div>';
  try {
    const data = await getJson('/api/workflow/logs');
    target.innerHTML = data.map(log => `
      <div class="item log-item ${escapeHtml(log.status)}">
        <div class="log-title">
          <strong>${escapeHtml(log.workflow)}</strong>
          <span class="status-badge ${escapeHtml(log.status)}">${escapeHtml(log.status)}</span>
        </div>
        <div class="log-fields">
          <span><b>执行时间：</b>${escapeHtml(log.time)}</span>
          <span><b>工作流名称：</b>${escapeHtml(log.workflow)}</span>
          <span><b>触发方式：</b>${escapeHtml(log.trigger)}</span>
          <span><b>执行状态：</b>${escapeHtml(log.status)}</span>
          <span class="log-summary"><b>结果摘要：</b>${escapeHtml(log.summary)}</span>
        </div>
      </div>
    `).join('');
  } catch (error) {
    target.innerHTML = `<div class="item error">接口调用失败：${escapeHtml(error.message)}</div>`;
  }
}

async function loadSqlExamples() {
  const target = el('sql-examples');
  target.innerHTML = '<div class="item">正在加载 SQL 示例...</div>';
  try {
    const data = await getJson('/api/sql/examples');
    target.innerHTML = data.examples.map(item => `
      <div class="item sql-item">
        <strong>${escapeHtml(item.title)}</strong>
        <small>${escapeHtml(item.business_value || item.value || '')}</small>
        <code>${escapeHtml(item.sql)}</code>
      </div>
    `).join('');
  } catch (error) {
    target.innerHTML = `<div class="item error">接口调用失败：${escapeHtml(error.message)}</div>`;
  }
}

async function loadAiRoadmap() {
  const target = el('ai-roadmap');
  target.innerHTML = '<div class="roadmap-card">正在加载 AI 路线...</div>';
  try {
    const data = await getJson('/api/ai/roadmap');
    target.innerHTML = data.roadmap.map(item => `
      <div class="roadmap-card">
        <strong>${escapeHtml(item.name)}</strong>
        <small>适用场景：${escapeHtml(item.scenario || item.scene || '')}</small>
        <span>${escapeHtml(item.business_value || item.value || '')}</span>
      </div>
    `).join('');
  } catch (error) {
    target.innerHTML = `<div class="roadmap-card error">接口调用失败：${escapeHtml(error.message)}</div>`;
  }
}

async function loadReport() {
  el('report').textContent = '正在生成日报...';
  try {
    const data = await getJson('/api/report/daily');
    el('report').textContent = data.report;
  } catch (error) {
    showError('report', error);
  }
}

async function runCommand(command) {
  el('command-result').textContent = '正在执行命令...';
  try {
    const data = await getJson('/api/bot/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, push_to_bot: false })
    });
    el('command-result').textContent = data.result;
  } catch (error) {
    showError('command-result', error);
  }
}

async function classifyException() {
  el('exception-ai').textContent = 'AI正在分析异常...';
  try {
    const data = await getJson('/api/ai/exception-classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: el('exception-text').value })
    });
    el('exception-ai').textContent = `${data.structured_output}

模型路由：${data.model_route.primary_model}
备用模型：${data.model_route.fallback_model}
选择原因：${data.model_route.reason}`;
  } catch (error) {
    showError('exception-ai', error);
  }
}

async function selectModel(taskType) {
  el('model-route').textContent = '正在选择模型路由...';
  try {
    const data = await getJson('/api/model-routing/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_type: taskType })
    });
    el('model-route').textContent = `任务：${data.task_name}
主模型：${data.primary_model}
备用模型：${data.fallback_model}
质量目标：${data.quality_target}
成本策略：${data.cost_strategy}
选择原因：${data.reason}`;
  } catch (error) {
    showError('model-route', error);
  }
}

async function askCustomerService() {
  el('customer-answer').textContent = 'AI客服正在回复...';
  try {
    const data = await getJson('/api/customer-service', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: el('customer-message').value,
        name: el('customer-name').value || '匿名客户',
        contact: el('customer-contact').value || null,
        save_lead: true
      })
    });
    el('customer-answer').textContent = `${data.answer}

识别意向：${data.intent_level}
需求摘要：${data.demand}`;
    await loadDashboard();
  } catch (error) {
    showError('customer-answer', error);
  }
}

async function loadFeishuDesign() {
  const schemaTarget = el('feishu-schema');
  const workflowTarget = el('feishu-workflows');
  schemaTarget.innerHTML = '<div class="item">正在加载飞书表结构...</div>';
  workflowTarget.innerHTML = '<div class="item">正在加载自动化规则...</div>';
  try {
    const data = await getJson('/api/feishu/design');
    schemaTarget.innerHTML = data.tables.map(table => `
      <div class="item">
        <strong>${escapeHtml(table.table_name)}</strong>
        <small>${escapeHtml(table.purpose)}</small>
        <ul>${table.fields.slice(0, 5).map(field => `<li>${escapeHtml(field.name)} | ${escapeHtml(field.type)} | ${escapeHtml(field.example)}</li>`).join('')}</ul>
      </div>
    `).join('');
    workflowTarget.innerHTML = data.workflows.map(workflow => `
      <div class="item">
        <strong>${escapeHtml(workflow.name)}</strong>
        <small>触发：${escapeHtml(workflow.trigger)}<br>动作：${escapeHtml(workflow.action)}<br>价值：${escapeHtml(workflow.business_value)}</small>
      </div>
    `).join('');
  } catch (error) {
    schemaTarget.innerHTML = `<div class="item error">接口调用失败：${escapeHtml(error.message)}</div>`;
    workflowTarget.innerHTML = '';
  }
}

Object.assign(window, {
  askCustomerService,
  classifyException,
  loadAiRoadmap,
  loadDashboard,
  loadEcommerceFlow,
  loadFeishuDesign,
  loadReport,
  loadSqlExamples,
  loadWorkflowLogs,
  runCommand,
  runFullFlow,
  runMockApi,
  selectModel
});

loadDashboard();
loadSqlExamples();
loadAiRoadmap();
loadFeishuDesign();
loadWorkflowLogs();
selectModel('daily_report');

