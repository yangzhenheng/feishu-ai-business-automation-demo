async function getJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function el(id) { return document.getElementById(id); }

async function loadDashboard() {
  const data = await getJson('/api/dashboard');
  const m = data.metrics;
  el('metrics').innerHTML = `
    <div class="metric"><span>订单总数</span><strong>${m.orders}</strong></div>
    <div class="metric"><span>未关闭异常</span><strong>${m.active_exceptions}</strong></div>
    <div class="metric"><span>库存预警</span><strong>${m.low_stock}</strong></div>
    <div class="metric"><span>未完成待办</span><strong>${m.open_todos}</strong></div>
    <div class="metric"><span>客户线索</span><strong>${m.open_leads}</strong></div>
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
      <small>当前库存：${i.current_stock}｜安全库存：${i.safety_stock}｜供应商：${i.supplier}｜仓库：${i.warehouse}</small>
    </div>
  `).join('') || '<p>暂无库存预警</p>';

  el('leads').innerHTML = data.leads.map(l => `
    <div class="item">
      <strong>${l.name} · ${l.intent_level}意向</strong>
      <small>${l.demand}<br>联系方式：${l.contact || '未留'}｜来源：${l.source}｜状态：${l.status}</small>
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
  el('customer-answer').textContent = data.answer;
  await loadDashboard();
}

loadDashboard().catch(err => alert(err.message));
