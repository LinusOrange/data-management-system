<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

const summary = ref({
  pending_reconciliation_count: 0,
  pending_invoice_count: 0,
  reconciliation_exception_count: 0,
  closed_loop_count: 0
})
const purchases = ref([])
const loading = ref(false)

const statusOptions = [
  { label: '未开票', value: 'not_invoiced' },
  { label: '部分开票', value: 'partially_invoiced' },
  { label: '已开票', value: 'invoiced' }
]

const filter = ref('all')

const filteredPurchases = computed(() => {
  if (filter.value === 'all') return purchases.value
  return purchases.value.filter((item) => item.reconciliation_status === filter.value)
})

const loadData = async () => {
  loading.value = true
  try {
    const [summaryResp, purchasesResp] = await Promise.all([
      axios.get('/api/dashboard/summary'),
      axios.get('/api/purchases')
    ])
    summary.value = summaryResp.data
    purchases.value = purchasesResp.data
  } catch (error) {
    console.error('load error', error)
  } finally {
    loading.value = false
  }
}

const updateInvoice = async (item, value) => {
  await axios.patch(`/api/purchases/${item.id}/invoice-status`, {
    invoice_status: value,
    operator: 'web-user',
    note: '前端更新开票状态'
  })
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <main class="page">
    <header class="header">
      <h1>票据数据对账系统</h1>
      <button class="refresh" @click="loadData">刷新数据</button>
    </header>

    <section class="kpis">
      <article class="card warn">
        <h3>未对账</h3>
        <p>{{ summary.pending_reconciliation_count }}</p>
      </article>
      <article class="card warn">
        <h3>未开票</h3>
        <p>{{ summary.pending_invoice_count }}</p>
      </article>
      <article class="card danger">
        <h3>异常</h3>
        <p>{{ summary.reconciliation_exception_count }}</p>
      </article>
      <article class="card ok">
        <h3>已闭环</h3>
        <p>{{ summary.closed_loop_count }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>采购条目</h2>
        <select v-model="filter">
          <option value="all">全部</option>
          <option value="pending">未对账</option>
          <option value="done">已对账</option>
          <option value="exception">异常</option>
        </select>
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>订单号/摘要</th>
            <th>产品/型号</th>
            <th>数量</th>
            <th>含税金额</th>
            <th>对账状态</th>
            <th>开票状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7">加载中...</td>
          </tr>
          <tr v-for="item in filteredPurchases" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.order_ref || '-' }}</td>
            <td>{{ item.item_model || '-' }}</td>
            <td>{{ item.qty || '-' }}</td>
            <td>{{ item.amount_tax_incl || '-' }}</td>
            <td>{{ item.reconciliation_status }}</td>
            <td>
              <select :value="item.invoice_status" @change="updateInvoice(item, $event.target.value)">
                <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </td>
          </tr>
          <tr v-if="!loading && filteredPurchases.length === 0">
            <td colspan="7">暂无数据，请先导入并执行对账</td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>
