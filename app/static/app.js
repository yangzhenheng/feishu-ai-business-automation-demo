async function getJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function el(id) { return document.getElementById(id); }
function safe(value) { return value === null || value === undefined || value === '' ? '未填写' : value; }

async function loadDashboard() {
  const data = await getJson('/api/dashboard');
  const m = data.metrics;
  el('metrics').innerHTML = `
    <div class="metric"><span>订单总数</span><strong>${m.orders}</strong><small>Orders</small></div>
    <div class="metric danger"><span>未关闭异常</span><strong>${m.active_exceptions}</strong><small>Exceptions</small></div>
    <div class="metric warning"><span>库存预警</span><strong>${m.low_stock}</strong><small>Low Stock</small></div>
    <div class="metric"><span>未完成待办</span><strong>${m.open_todos}</strong><small>Todos</small></div>
    <div class="metric"><span>客户线索</span><strong>${m.open_leads}</strong><small>Leads</small></div>
  `;

  el('exceptions').innerHTML = data.exceptions.map(e => `
    <div class="item">
      <strong>${e.exception_no} · ${e.exception_type} · ${e.priority}</strong>
      <small>${e.order_no}｜负责人：${e.owner}｜状态：${e.status}<br>${e.reason}</small>
    </div>
  `).join('') || '<p>暂无异常</p>';

  el('low-stock').innerHTML = data.low_stock.map(i => `
    <div class="item">
      <strong>${i.sku} · ${i.product_name}</strong>
      <small>当前库存：${i.current_stock}｜安全库存：${i.safety_stock}｜缺口：${i.safety_stock - i.current_stock}｜供应商：${i.supplier}｜仓库：${i.warehouse}</small>
    </div>
  `).join('') || '<p>暂无库存预警</p>';

  el('leads').innerHTML = data.leads.map(l => `
    <div class="item">
      <strong>${l.name} · ${l.intent_level}意向</strong>
      <small>${l.demand}<br>联系方式：${safe(l.contact)}｜来源：${l.source}｜状态：${l.status}</small>
    </div>
  `).join('') || '<p>暂无客户线索</p>';
}

async function loadReport() {
  el('report').textContent = '正在生成日报...';
  const data = await getJson('/api/report/daily');
  el('report').textContent = data.report;
}

async function runCommand(command) {
  el('command-result').textContent = '正在执行命令...';
  const data = await getJson('/api/bot/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command, push_to_bot: false })
  });
  el('command-result').textContent = data.result;
}

async function classifyException() {
  el('exception-ai').textContent = 'AI正在分析异常...';
  const data = await getJson('/api/ai/exception-classify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: el('exception-text').value })
  });
  el('exception-ai').textContent = `${data.structured_output}\n\n模型路由：${data.model_route.primary_model}\n备用模型：${data.model_route.fallback_model}\n选择原因：${data.model_route.reason}`;
}

async function selectModel(taskType) {
  el('model-route').textContent = '正在选择模型路由...';
  const data = await getJson('/api/model-routing/select', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_type: taskType })
  });
  el('model-route').textContent = `任务：${data.task_name}\n主模型：${data.primary_model}\n备用模型：${data.fallback_model}\n质量目标：${data.quality_target}\n成本策略：${data.cost_strategy}\n选择原因：${data.reason}`;
}

async function askCustomerService() {
  el('customer-answer').textContent = 'AI客服正在回复...';
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
  el('customer-answer').textContent = `${data.answer}\n\n识别意向：${data.intent_level}\n需求摘要：${data.demand}`;
  await loadDashboard();
}

async function loadFeishuDesign() {
  const data = await getJson('/api/feishu/design');
  el('feishu-schema').innerHTML = data.tables.map(t => `
    <div class="item">
      <strong>${t.table_name}</strong>
      <small>${t.purpose}</small>
      <ul>${t.fields.slice(0, 5).map(f => `<li>${f.name}｜${f.type}｜${f.example}</li>`).join('')}</ul>
    </div>
  `).join('');
  el('feishu-workflows').innerHTML = data.workflows.map(w => `
    <div class="item">
      <strong>${w.name}</strong>
      <small>触发：${w.trigger}<br>动作：${w.action}<br>价值：${w.business_value}</small>
    </div>
  `).join('');
}

loadDashboard().catch(err => alert(err.message));
loadFeishuDesign().catch(() => {});
selectModel('daily_report').catch(() => {});
