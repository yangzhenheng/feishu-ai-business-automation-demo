CREATE DATABASE IF NOT EXISTS flowpilot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE flowpilot;

CREATE TABLE IF NOT EXISTS orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id VARCHAR(64) NOT NULL UNIQUE,
  shop_name VARCHAR(120) NOT NULL,
  customer_name VARCHAR(80),
  sku VARCHAR(64) NOT NULL,
  product_name VARCHAR(120) NOT NULL,
  quantity INT NOT NULL,
  paid_amount DECIMAL(10,2) NOT NULL,
  order_status VARCHAR(32) NOT NULL,
  buyer_note VARCHAR(500),
  owner VARCHAR(50),
  created_at DATETIME NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_orders_shop_created (shop_name, created_at),
  INDEX idx_orders_sku (sku)
);

CREATE TABLE IF NOT EXISTS inventory (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  sku VARCHAR(64) NOT NULL,
  product_name VARCHAR(120) NOT NULL,
  warehouse VARCHAR(80) NOT NULL,
  available_stock INT NOT NULL,
  locked_stock INT NOT NULL DEFAULT 0,
  safety_stock INT NOT NULL,
  supplier VARCHAR(120),
  replenishment_days INT DEFAULT 7,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_inventory_sku_warehouse (sku, warehouse)
);

CREATE TABLE IF NOT EXISTS exceptions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  exception_no VARCHAR(64) NOT NULL UNIQUE,
  order_id VARCHAR(64),
  exception_type VARCHAR(64) NOT NULL,
  reason VARCHAR(500) NOT NULL,
  priority VARCHAR(16) NOT NULL,
  owner VARCHAR(50),
  status VARCHAR(32) NOT NULL,
  next_action VARCHAR(500),
  created_at DATETIME NOT NULL,
  closed_at DATETIME NULL,
  INDEX idx_exceptions_order (order_id),
  INDEX idx_exceptions_status_priority (status, priority)
);

CREATE TABLE IF NOT EXISTS customer_leads (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  lead_id VARCHAR(64) NOT NULL UNIQUE,
  customer_name VARCHAR(80) NOT NULL,
  contact VARCHAR(120),
  source VARCHAR(80) NOT NULL,
  demand VARCHAR(500) NOT NULL,
  intent_level VARCHAR(16) NOT NULL,
  follow_status VARCHAR(32) NOT NULL,
  recommended_owner VARCHAR(50),
  created_at DATETIME NOT NULL,
  INDEX idx_leads_intent_status (intent_level, follow_status)
);

CREATE TABLE IF NOT EXISTS ai_reports (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  report_id VARCHAR(64) NOT NULL UNIQUE,
  report_date DATE NOT NULL,
  report_type VARCHAR(32) NOT NULL,
  summary TEXT NOT NULL,
  risk_count INT NOT NULL DEFAULT 0,
  model_name VARCHAR(80),
  pushed_to_feishu TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL,
  UNIQUE KEY uk_ai_reports_date_type (report_date, report_type)
);

CREATE TABLE IF NOT EXISTS workflow_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  workflow_id VARCHAR(64) NOT NULL,
  workflow_name VARCHAR(120) NOT NULL,
  trigger_source VARCHAR(120) NOT NULL,
  related_object_type VARCHAR(64),
  related_object_id VARCHAR(64),
  action_result VARCHAR(32) NOT NULL,
  detail VARCHAR(500),
  created_at DATETIME NOT NULL,
  INDEX idx_workflow_related (related_object_type, related_object_id)
);

CREATE TABLE IF NOT EXISTS finance_reconcile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  reconcile_id VARCHAR(64) NOT NULL UNIQUE,
  order_id VARCHAR(64) NOT NULL,
  shop_name VARCHAR(120) NOT NULL,
  order_amount DECIMAL(10,2) NOT NULL,
  received_amount DECIMAL(10,2) NOT NULL,
  diff_amount DECIMAL(10,2) NOT NULL,
  diff_reason VARCHAR(300),
  status VARCHAR(32) NOT NULL,
  created_at DATETIME NOT NULL,
  INDEX idx_finance_order (order_id),
  INDEX idx_finance_diff (diff_amount)
);

CREATE TABLE IF NOT EXISTS logistics_tracking (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  tracking_no VARCHAR(80) NOT NULL UNIQUE,
  order_id VARCHAR(64) NOT NULL,
  carrier VARCHAR(50) NOT NULL,
  logistics_status VARCHAR(50) NOT NULL,
  is_exception TINYINT(1) NOT NULL DEFAULT 0,
  exception_reason VARCHAR(300),
  suggested_action VARCHAR(300),
  updated_at DATETIME NOT NULL,
  INDEX idx_logistics_order (order_id),
  INDEX idx_logistics_exception (is_exception)
);

INSERT INTO orders(order_id, shop_name, customer_name, sku, product_name, quantity, paid_amount, order_status, buyer_note, owner, created_at)
VALUES
('SHOP-20260626-001', '抖音小店-广州女装直播间', '陈小姐', 'DRS-FLORAL-M', '碎花收腰连衣裙 M', 2, 398.00, '已支付', '周末前想收到', '运营-小周', '2026-06-26 10:18:00'),
('SHOP-20260626-004', '抖音小店-广州女装直播间', '团购客户', 'HOODIE-GRY-L', '灰色短款卫衣 L', 5, 745.00, '已支付', '团购急单，少发漏发请提前联系', '运营-小周', '2026-06-26 11:23:00'),
('SHOP-20260626-005', '天猫店-夏季通勤女装', '林女士', 'DRS-BLACK-S', '黑色通勤连衣裙 S', 1, 219.00, '售后中', '换小一码', '客服-阿敏', '2026-06-26 11:45:00')
ON DUPLICATE KEY UPDATE order_status = VALUES(order_status);

INSERT INTO inventory(sku, product_name, warehouse, available_stock, locked_stock, safety_stock, supplier, replenishment_days)
VALUES
('DRS-FLORAL-M', '碎花收腰连衣裙 M', '广州仓', 42, 18, 80, '广州番禺连衣裙工厂', 5),
('HOODIE-GRY-L', '灰色短款卫衣 L', '佛山仓', 22, 8, 100, '佛山针织供应商', 9),
('TEE-COTTON-WHT-L', '纯棉基础白T恤 L', '广州仓', 260, 35, 120, '中山T恤工厂', 4)
ON DUPLICATE KEY UPDATE available_stock = VALUES(available_stock), safety_stock = VALUES(safety_stock);

INSERT INTO exceptions(exception_no, order_id, exception_type, reason, priority, owner, status, next_action, created_at)
VALUES
('EXP-20260626-001', 'SHOP-20260626-004', '物流延迟', '佛山仓晚班未完成交接，团购订单存在交期风险', 'P1', '仓储-阿强', '处理中', '升级仓储负责人并同步客服话术', '2026-06-26 12:10:00'),
('EXP-20260626-002', 'SHOP-20260626-005', '退换货', '换码订单需等待原包裹退回', 'P2', '客服-阿敏', '待客服确认', '确认小码库存并更新售后单', '2026-06-26 12:20:00')
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO customer_leads(lead_id, customer_name, contact, source, demand, intent_level, follow_status, recommended_owner, created_at)
VALUES
('CRM-20260626-001', '直播间团购客户-陈小姐', 'wechat: chen-demo', '抖音直播间', '公司活动采购80件连衣裙', '高', '待销售跟进', '华南大客户销售', '2026-06-26 12:30:00'),
('CRM-20260626-002', '天猫复购客户-林女士', 'tmall-id-demo', '天猫店客服咨询', '关注半身裙和T恤搭配', '中', '私域运营跟进', '会员运营', '2026-06-26 12:35:00')
ON DUPLICATE KEY UPDATE follow_status = VALUES(follow_status);

INSERT INTO ai_reports(report_id, report_date, report_type, summary, risk_count, model_name, pushed_to_feishu, created_at)
VALUES
('AIR-20260626-001', '2026-06-26', 'daily', '今日直播间订单增长，卫衣 L 码和碎花连衣裙 M 码低库存，团购订单存在物流交期风险。', 3, 'gpt-4o-mini/mock-router', 1, '2026-06-26 18:00:00')
ON DUPLICATE KEY UPDATE summary = VALUES(summary);

INSERT INTO workflow_logs(workflow_id, workflow_name, trigger_source, related_object_type, related_object_id, action_result, detail, created_at)
VALUES
('WF-LOW-STOCK', '库存不足采购补货审批', 'inventory.available_stock < safety_stock', 'sku', 'HOODIE-GRY-L', 'created', '已创建采购补货审批并通知运营', '2026-06-26 12:40:00'),
('WF-FIN-DIFF', '财务差异复核审批', 'finance_reconcile.diff_amount <> 0', 'order', 'SHOP-20260626-004', 'created', '优惠券承担方待运营确认', '2026-06-26 12:45:00');

INSERT INTO finance_reconcile(reconcile_id, order_id, shop_name, order_amount, received_amount, diff_amount, diff_reason, status, created_at)
VALUES
('FIN-20260626-002', 'SHOP-20260626-004', '抖音小店-广州女装直播间', 745.00, 700.00, 45.00, '直播间优惠券承担方未确认', '待复核', '2026-06-26 13:00:00'),
('FIN-20260626-003', 'SHOP-20260626-005', '天猫店-夏季通勤女装', 219.00, 0.00, 219.00, '售后换货中，平台暂缓结算', '待售后完成', '2026-06-26 13:05:00')
ON DUPLICATE KEY UPDATE status = VALUES(status);

INSERT INTO logistics_tracking(tracking_no, order_id, carrier, logistics_status, is_exception, exception_reason, suggested_action, updated_at)
VALUES
('SF202606260089', 'SHOP-20260626-004', '顺丰速运', '揽收延迟', 1, '佛山仓晚班未完成交接', '升级仓储负责人，客服同步买家预计发货时间', '2026-06-26 13:10:00'),
('ZT202606260778', 'SHOP-20260626-005', '中通快递', '退换货返回中', 1, '售后换码订单', '客服确认换货 SKU 库存', '2026-06-26 13:12:00')
ON DUPLICATE KEY UPDATE logistics_status = VALUES(logistics_status);
