<template>
  <section class="panel">
    <div class="panel-head">
      <h2>数据库管理（purchase_item）</h2>
      <select v-model="state.purchaseFilter">
        <option value="all">全部</option>
        <option value="pending">未对账</option>
        <option value="done">已对账</option>
        <option value="exception">异常</option>
      </select>
    </div>
    <table>
      <thead>
        <tr><th>名称</th><th>货号</th><th>数量</th><th>金额</th><th>订单号</th><th>对账</th><th>开票</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="item in displayRows" :key="item.id">
          <td>{{ item.name || '-' }}</td><td>{{ item.item_code || '-' }}</td><td>{{ item.qty || '-' }}</td><td>{{ item.amount || '-' }}</td><td>{{ item.order_no || '-' }}</td>
          <td>
            <select :value="item.reconciliation_status" @change="updateReconciliation(item, $event.target.value)">
              <option v-for="s in reconOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
          </td>
          <td>
            <select :value="item.invoice_status" @change="updateInvoice(item, $event.target.value)">
              <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
          </td>
          <td><button class="danger-btn" @click="removePurchase(item.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useAppData } from '../composables/useAppData'

const { state, reconOptions, statusOptions, updateInvoice, updateReconciliation, removePurchase } = useAppData()

const displayRows = computed(() => {
  const rows = state.purchaseFilter === 'all'
    ? state.purchases
    : state.purchases.filter((item) => item.reconciliation_status === state.purchaseFilter)

  return rows.map((item) => ({
    id: item.id,
    name: item.item_name,
    item_code: item.item_model,
    qty: item.qty,
    amount: item.amount_tax_incl,
    order_no: item.order_ref,
    reconciliation_status: item.reconciliation_status,
    invoice_status: item.invoice_status
  }))
})
</script>
