# ERP / WMS / CRM 模拟 API 设计

本项目提供一组模拟 API，用于展示低代码开发工程师如何对接店铺、仓储、物流、财务和 CRM 系统。

## 店铺 API

- `GET /api/mock/shop/orders`
- `POST /api/mock/shop/orders/sync`

作用：模拟从抖音小店、天猫店、拼多多店同步订单到 ERP 订单池。同步时识别急单、售后中、待客服确认等异常。

## WMS API

- `POST /api/mock/wms/inventory/check`

作用：检查广州仓和佛山仓的 SKU 可用库存。如果可用库存低于安全库存，返回缺口数量和采购补货建议。

## 物流 API

- `POST /api/mock/logistics/track`

作用：模拟查询顺丰、圆通、中通等运单状态，识别揽收延迟、退换货返回、少发漏发等风险。

## 财务 API

- `POST /api/mock/finance/reconcile`

作用：模拟店铺账单和 ERP 订单对账，返回订单金额、已回款金额、差异金额和差异原因。

## CRM API

- `POST /api/mock/crm/leads`

作用：把直播间团购、店铺客服咨询和售后工单沉淀为客户线索，并推荐销售、会员运营或售后负责人。
