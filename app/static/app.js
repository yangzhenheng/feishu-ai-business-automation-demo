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
        <strong>${item.exception_no} | ${item.exception_type} | ${item.priority}</strong>
        <small>${item.order_no} | 负责人：${item.owner} | 状态：${item.status}<br>${item.reason}</small>
      </div>
    `).join('') || '<p>暂无异常</p>';

    el('low-stock').innerHTML = data.low_stock.map(item => `
      <div class="item">
        <strong>${item.sku} | ${item.product_name}</strong>
        <small>当前库存：${item.current_stock} | 安全库存：${item.safety_stock} | 缺口：${item.safety_stock - item.current_stock} | 供应商：${item.supplier} | 仓库：${item.warehouse}</small>
      </div>
    `).join('') || '<p>暂无库存预警</p>';

    el('leads').innerHTML = data.leads.map(item => `
      <div class="item">
        <strong>${item.name} | ${item.intent_level}意向</strong>
        <small>${item.demand}<br>联系方式：${safe(item.contact)} | 来源：${item.source} | 状态：${item.status}</small>
      </div>
    `).join('') || '<p>暂无客户线索</p>';
  } catch (error) {
    alert(`Dashboard 加载失败：${error.message}`);
  }
}

async function loadEcommerceFlow() {
  const flowTarget = el('ecommerce-flow');
  const valueTarget = el('ecommerce-values');
  flowTarget.innerHTML = '<div class="flow-step"><strong>正在加载业务闭环...</strong></div>';
  valueTarget.innerHTML = '';

  try {
    const data = await getJson('/api/ecommerce/flow');
    flowTarget.innerHTML = data.flow.map((step, index) => `
      <div class="flow-step">
        <span>${String(index + 1).padStart(2, '0')}</span>
        <strong>${step}</strong>
        <small>${data.scene}</small>
      </div>
    `).join('');
    valueTarget.innerHTML = `<div class="value-card">${data.business_value}</div>`;
  } catch (error) {
    flowTarget.innerHTML = `<div class="flow-step error">接口调用失败：${error.message}</div>`;
  }
}

function renderMockApiResult(type, data) {
  if (type === 'sync') {
    return `模块：${data.module}
同步订单：${data.synced_count}
异常订单：${data.exception_count}
下一步：${data.next_action}`;
  }

  if (type === 'inventory') {
    const rows = data.low_stock.map(item => `${item.sku} ${item.product}
当前库存：${item.stock}
安全库存：${item.safe_stock}
缺口：${item.gap}`).join('\n\n');
    return `模块：${data.module}

${rows}

建议：${data.next_action}`;
  }

  if (type === 'logistics') {
    return `模块：${data.module}
运单号：${data.tracking_no}
状态：${data.status}
原因：${data.reason}
下一步：${data.next_action}`;
  }

  if (type === 'finance') {
    return `模块：${data.module}
订单金额：${data.order_amount}
已回款金额：${data.received_amount}
差异金额：${data.difference}
差异原因：${data.reason}
下一步：${data.next_action}`;
  }

  if (type === 'crm') {
    const rows = data.leads.map(item => `${item.name} | 来源：${item.source} | 意向：${item.intent} | 状态：${item.status}`).join('\n');
    return `模块：${data.module}
${rows}
下一步：${data.next_action}`;
  }

  return JSON.stringify(data, null, 2);
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
    el('mock-api-result').textContent = renderMockApiResult(type, data);
  } catch (error) {
    showError('mock-api-result', error);
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
        <small>${escapeHtml(item.business_value)}</small>
        <code>${escapeHtml(item.sql)}</code>
      </div>
    `).join('');
  } catch (error) {
    target.innerHTML = `<div class="item error">接口调用失败：${error.message}</div>`;
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
        <small>适用场景：${escapeHtml(item.scenario)}</small>
        <span>${escapeHtml(item.business_value)}</span>
      </div>
    `).join('');
  } catch (error) {
    target.innerHTML = `<div class="roadmap-card error">接口调用失败：${error.message}</div>`;
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
        <strong>${table.table_name}</strong>
        <small>${table.purpose}</small>
        <ul>${table.fields.slice(0, 5).map(field => `<li>${field.name} | ${field.type} | ${field.example}</li>`).join('')}</ul>
      </div>
    `).join('');
    workflowTarget.innerHTML = data.workflows.map(workflow => `
      <div class="item">
        <strong>${workflow.name}</strong>
        <small>触发：${workflow.trigger}<br>动作：${workflow.action}<br>价值：${workflow.business_value}</small>
      </div>
    `).join('');
  } catch (error) {
    schemaTarget.innerHTML = `<div class="item error">接口调用失败：${error.message}</div>`;
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
  runCommand,
  runMockApi,
  selectModel
});

loadDashboard();
loadEcommerceFlow();
loadSqlExamples();
loadAiRoadmap();
loadFeishuDesign();
selectModel('daily_report');
