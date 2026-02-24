<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

const activeTab = ref('dashboard')
const loading = ref(false)
const message = ref('')

const summary = ref({
  pending_reconciliation_count: 0,
  pending_invoice_count: 0,
  reconciliation_exception_count: 0,
  closed_loop_count: 0
})

const purchases = ref([])
const batches = ref([])
const previewRows = ref([])
const previewBatchId = ref('')

const uploadForm = ref({ source_type: 'statement', uploaded_by: '', file: null })
const reconciliationForm = ref({ statement_batch_id: '', inbound_batch_id: '' })

const statusOptions = [
  { label: '未开票', value: 'not_invoiced' },
  { label: '部分开票', value: 'partially_invoiced' },
  { label: '已开票', value: 'invoiced' }
]
const reconOptions = [
  { label: '未对账', value: 'pending' },
  { label: '已对账', value: 'done' },
  { label: '异常', value: 'exception' }
]

const purchaseFilter = ref('all')
const filteredPurchases = computed(() => purchaseFilter.value === 'all'
  ? purchases.value
  : purchases.value.filter((item) => item.reconciliation_status === purchaseFilter.value))

const displayRows = computed(() => filteredPurchases.value.map((item) => ({
  id: item.id,
  name: item.item_name,
  item_code: item.item_model,
  qty: item.qty,
  amount: item.amount_tax_incl,
  order_no: item.order_ref,
  reconciliation_status: item.reconciliation_status,
  invoice_status: item.invoice_status
})))

const loadSummary = async () => { summary.value = (await axios.get('/api/dashboard/summary')).data }
const loadPurchases = async () => { purchases.value = (await axios.get('/api/purchases')).data }
const loadBatches = async () => { batches.value = (await axios.get('/api/imports')).data }

const loadAll = async () => {
  loading.value = true
  message.value = ''
  try {
    await Promise.all([loadSummary(), loadPurchases(), loadBatches()])
  } catch (error) {
    message.value = `加载失败：${error?.message || '未知错误'}`
  } finally {
    loading.value = false
  }
}

const onFileChange = (event) => { uploadForm.value.file = event.target.files?.[0] || null }

const uploadFile = async () => {
  if (!uploadForm.value.file) return (message.value = '请先选择要上传的文件')
  const formData = new FormData()
  formData.append('source_type', uploadForm.value.source_type)
  if (uploadForm.value.uploaded_by) formData.append('uploaded_by', uploadForm.value.uploaded_by)
  formData.append('file', uploadForm.value.file)

  loading.value = true
  try {
    const { data } = await axios.post('/api/imports/upload', formData)
    message.value = `上传成功，批次 #${data.id}，已自动解析`
    previewBatchId.value = String(data.id)
    await Promise.all([loadBatches(), loadPreview()])
  } catch (error) {
    message.value = `上传失败：${error?.response?.data?.detail || error.message}`
  } finally {
    loading.value = false
  }
}

const loadPreview = async () => {
  if (!previewBatchId.value) return
  try {
    const { data } = await axios.get(`/api/imports/${previewBatchId.value}/preview`)
    previewRows.value = data
  } catch (error) {
    message.value = `预览失败：${error?.response?.data?.detail || error.message}`
  }
}

const runReconciliation = async () => {
  if (!reconciliationForm.value.statement_batch_id || !reconciliationForm.value.inbound_batch_id) {
    return (message.value = '请选择对账单批次和入库单批次')
  }
  loading.value = true
  try {
    await axios.post('/api/reconciliation/run', null, {
      params: {
        statement_batch_id: reconciliationForm.value.statement_batch_id,
        inbound_batch_id: reconciliationForm.value.inbound_batch_id
      }
    })
    message.value = '对账任务已执行'
    await loadAll()
  } catch (error) {
    message.value = `执行对账失败：${error?.response?.data?.detail || error.message}`
  } finally {
    loading.value = false
  }
}

const updateInvoice = async (item, value) => {
  await axios.patch(`/api/purchases/${item.id}/invoice-status`, { invoice_status: value, operator: 'web-user' })
  await loadAll()
}

const updateReconciliation = async (item, value) => {
  await axios.patch(`/api/purchases/${item.id}/reconciliation-status`, { reconciliation_status: value, operator: 'web-user' })
  await loadAll()
}

const removePurchase = async (itemId) => {
  await axios.delete(`/api/purchases/${itemId}`)
  await loadAll()
}

onMounted(loadAll)
</script>

<template>
  <main class="page">
    <header class="topbar">
      <h1>票据数据对账系统</h1>
      <nav class="nav">
        <button :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">系统看板</button>
        <button :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">上传文件对账</button>
        <button :class="{ active: activeTab === 'db' }" @click="activeTab = 'db'">数据库管理</button>
      </nav>
    </header>

    <p v-if="message" class="msg">{{ message }}</p>

    <section v-if="activeTab === 'dashboard'">
      <div class="kpis">
        <article class="card warn"><h3>未对账</h3><p>{{ summary.pending_reconciliation_count }}</p></article>
        <article class="card warn"><h3>未开票</h3><p>{{ summary.pending_invoice_count }}</p></article>
        <article class="card danger"><h3>异常</h3><p>{{ summary.reconciliation_exception_count }}</p></article>
        <article class="card ok"><h3>已闭环</h3><p>{{ summary.closed_loop_count }}</p></article>
      </div>
    </section>

    <section v-else-if="activeTab === 'upload'" class="panel">
      <h2>上传文件并自动解析</h2>
      <div class="form-grid">
        <label>文件类型
          <select v-model="uploadForm.source_type">
            <option value="statement">对账单（statement）</option>
            <option value="inbound">入库单（inbound）</option>
          </select>
        </label>
        <label>上传人
          <input v-model="uploadForm.uploaded_by" placeholder="可选" />
        </label>
        <label class="full">选择文件<input type="file" @change="onFileChange" /></label>
      </div>
      <button class="primary" :disabled="loading" @click="uploadFile">上传并解析</button>

      <hr />
      <h3>数据预览（名称 / 货号 / 数量 / 金额 / 订单号）</h3>
      <div class="panel-head">
        <select v-model="previewBatchId">
          <option value="">选择批次</option>
          <option v-for="b in batches" :key="b.id" :value="String(b.id)">#{{ b.id }} - {{ b.source_type }}</option>
        </select>
        <button class="refresh" @click="loadPreview">加载预览</button>
      </div>
      <table>
        <thead>
          <tr><th>名称</th><th>货号</th><th>数量</th><th>金额</th><th>订单号</th></tr>
        </thead>
        <tbody>
          <tr v-for="row in previewRows" :key="`${row.row_no}-${row.order_no || ''}`">
            <td>{{ row.name || '-' }}</td>
            <td>{{ row.item_code || '-' }}</td>
            <td>{{ row.qty || '-' }}</td>
            <td>{{ row.amount || '-' }}</td>
            <td>{{ row.order_no || '-' }}</td>
          </tr>
        </tbody>
      </table>

      <hr />
      <h3>执行对账任务</h3>
      <div class="form-grid">
        <label>对账单批次
          <select v-model="reconciliationForm.statement_batch_id">
            <option value="">请选择</option>
            <option v-for="b in batches.filter(x => x.source_type === 'statement')" :key="b.id" :value="b.id">#{{ b.id }}</option>
          </select>
        </label>
        <label>入库单批次
          <select v-model="reconciliationForm.inbound_batch_id">
            <option value="">请选择</option>
            <option v-for="b in batches.filter(x => x.source_type === 'inbound')" :key="b.id" :value="b.id">#{{ b.id }}</option>
          </select>
        </label>
      </div>
      <button class="primary" :disabled="loading" @click="runReconciliation">运行对账</button>
    </section>

    <section v-else class="panel">
      <div class="panel-head">
        <h2>数据库管理（purchase_item）</h2>
        <select v-model="purchaseFilter">
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
            <td>{{ item.name || '-' }}</td>
            <td>{{ item.item_code || '-' }}</td>
            <td>{{ item.qty || '-' }}</td>
            <td>{{ item.amount || '-' }}</td>
            <td>{{ item.order_no || '-' }}</td>
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
  </main>
</template>
