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

const uploadForm = ref({
  source_type: 'statement',
  uploaded_by: '',
  file: null
})

const reconciliationForm = ref({
  statement_batch_id: '',
  inbound_batch_id: ''
})

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

const filteredPurchases = computed(() => {
  if (purchaseFilter.value === 'all') return purchases.value
  return purchases.value.filter((item) => item.reconciliation_status === purchaseFilter.value)
})

const loadSummary = async () => {
  const { data } = await axios.get('/api/dashboard/summary')
  summary.value = data
}

const loadPurchases = async () => {
  const { data } = await axios.get('/api/purchases')
  purchases.value = data
}

const loadBatches = async () => {
  const { data } = await axios.get('/api/imports')
  batches.value = data
}

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

const onFileChange = (event) => {
  uploadForm.value.file = event.target.files?.[0] || null
}

const uploadFile = async () => {
  if (!uploadForm.value.file) {
    message.value = '请先选择要上传的文件'
    return
  }
  const formData = new FormData()
  formData.append('source_type', uploadForm.value.source_type)
  if (uploadForm.value.uploaded_by) formData.append('uploaded_by', uploadForm.value.uploaded_by)
  formData.append('file', uploadForm.value.file)

  try {
    loading.value = true
    await axios.post('/api/imports/upload', formData)
    message.value = '文件上传成功，已创建导入批次'
    uploadForm.value.file = null
    await loadBatches()
  } catch (error) {
    message.value = `上传失败：${error?.response?.data?.detail || error.message}`
  } finally {
    loading.value = false
  }
}

const runReconciliation = async () => {
  if (!reconciliationForm.value.statement_batch_id || !reconciliationForm.value.inbound_batch_id) {
    message.value = '请选择对账单批次和入库单批次'
    return
  }

  try {
    loading.value = true
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
  await axios.patch(`/api/purchases/${item.id}/invoice-status`, {
    invoice_status: value,
    operator: 'web-user',
    note: '前端更新开票状态'
  })
  await loadAll()
}

const updateReconciliation = async (item, value) => {
  await axios.patch(`/api/purchases/${item.id}/reconciliation-status`, {
    reconciliation_status: value,
    operator: 'web-user',
    note: '数据库管理页更新对账状态'
  })
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

      <section class="panel">
        <div class="panel-head">
          <h2>采购条目概览</h2>
          <button class="refresh" :disabled="loading" @click="loadAll">刷新数据</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>订单号/摘要</th><th>产品/型号</th><th>数量</th><th>含税金额</th><th>对账状态</th><th>开票状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in purchases.slice(0, 10)" :key="item.id">
              <td>{{ item.id }}</td><td>{{ item.order_ref || '-' }}</td><td>{{ item.item_model || '-' }}</td>
              <td>{{ item.qty || '-' }}</td><td>{{ item.amount_tax_incl || '-' }}</td>
              <td>{{ item.reconciliation_status }}</td><td>{{ item.invoice_status }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>

    <section v-else-if="activeTab === 'upload'" class="panel">
      <h2>上传文件进行对账</h2>
      <div class="form-grid">
        <label>文件类型
          <select v-model="uploadForm.source_type">
            <option value="statement">对账单（statement）</option>
            <option value="inbound">入库单（inbound）</option>
          </select>
        </label>
        <label>上传人
          <input v-model="uploadForm.uploaded_by" placeholder="可选：姓名/账号" />
        </label>
        <label class="full">选择文件
          <input type="file" @change="onFileChange" />
        </label>
      </div>
      <button class="primary" :disabled="loading" @click="uploadFile">上传并创建批次</button>

      <hr />

      <h3>执行对账任务</h3>
      <div class="form-grid">
        <label>对账单批次
          <select v-model="reconciliationForm.statement_batch_id">
            <option value="">请选择</option>
            <option v-for="b in batches.filter(x => x.source_type === 'statement')" :key="b.id" :value="b.id">
              #{{ b.id }} - {{ b.file_name }}
            </option>
          </select>
        </label>
        <label>入库单批次
          <select v-model="reconciliationForm.inbound_batch_id">
            <option value="">请选择</option>
            <option v-for="b in batches.filter(x => x.source_type === 'inbound')" :key="b.id" :value="b.id">
              #{{ b.id }} - {{ b.file_name }}
            </option>
          </select>
        </label>
      </div>
      <button class="primary" :disabled="loading" @click="runReconciliation">运行对账</button>

      <h3>导入批次列表</h3>
      <table>
        <thead><tr><th>ID</th><th>来源</th><th>文件</th><th>状态</th><th>上传时间</th></tr></thead>
        <tbody>
          <tr v-for="b in batches" :key="b.id">
            <td>{{ b.id }}</td><td>{{ b.source_type }}</td><td>{{ b.file_name }}</td><td>{{ b.parse_status }}</td><td>{{ b.uploaded_at }}</td>
          </tr>
        </tbody>
      </table>
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
          <tr>
            <th>ID</th><th>订单号/摘要</th><th>产品/型号</th><th>数量</th><th>对账状态</th><th>开票状态</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredPurchases" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.order_ref || '-' }}</td>
            <td>{{ item.item_model || '-' }}</td>
            <td>{{ item.qty || '-' }}</td>
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
            <td>
              <button class="danger-btn" @click="removePurchase(item.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>
