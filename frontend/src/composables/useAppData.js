import { reactive } from 'vue'
import axios from 'axios'

const state = reactive({
  loading: false,
  message: '',
  summary: {
    pending_reconciliation_count: 0,
    pending_invoice_count: 0,
    reconciliation_exception_count: 0,
    closed_loop_count: 0
  },
  purchases: [],
  batches: [],
  previewRows: [],
  previewBatchId: '',
  managedInboundRows: [],
  managedStatementRows: [],
  reconciliationResults: { success: [], failed_diff: [], failed_statement_only: [], failed_inbound_only: [] },
  uploadForm: { source_type: 'statement', uploaded_by: '', file: null },
  reconciliationForm: { statement_batch_id: '', inbound_batch_id: '' },
  purchaseFilter: 'all'
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

const loadSummary = async () => { state.summary = (await axios.get('/api/dashboard/summary')).data }
const loadPurchases = async () => { state.purchases = (await axios.get('/api/purchases')).data }
const loadBatches = async () => { state.batches = (await axios.get('/api/imports')).data }
const loadManagement = async () => {
  const { data } = await axios.get('/api/imports/manage/overview')
  state.managedInboundRows = data.inbound_rows
  state.managedStatementRows = data.statement_rows
}
const loadReconciliationResults = async () => {
  const params = {}
  if (state.reconciliationForm.statement_batch_id && state.reconciliationForm.inbound_batch_id) {
    params.statement_batch_id = state.reconciliationForm.statement_batch_id
    params.inbound_batch_id = state.reconciliationForm.inbound_batch_id
  }
  const { data } = await axios.get('/api/reconciliation/results', { params })
  state.reconciliationResults = data
}

const loadAll = async () => {
  state.loading = true
  state.message = ''
  try {
    await Promise.all([loadSummary(), loadPurchases(), loadBatches(), loadManagement(), loadReconciliationResults()])
  } catch (error) {
    state.message = `加载失败：${error?.message || '未知错误'}`
  } finally {
    state.loading = false
  }
}

const onFileChange = (event) => { state.uploadForm.file = event.target.files?.[0] || null }

const uploadFile = async () => {
  if (!state.uploadForm.file) return (state.message = '请先选择要上传的文件')
  const formData = new FormData()
  formData.append('source_type', state.uploadForm.source_type)
  if (state.uploadForm.uploaded_by) formData.append('uploaded_by', state.uploadForm.uploaded_by)
  formData.append('file', state.uploadForm.file)

  state.loading = true
  try {
    const { data } = await axios.post('/api/imports/upload', formData)
    state.message = data.parse_status === 'failed'
      ? `上传完成但解析失败（批次 #${data.id}）：${data.parse_error || '未知原因'}`
      : `上传成功，批次 #${data.id}，已自动解析`
    state.previewBatchId = String(data.id)
    await Promise.all([loadBatches(), loadManagement(), loadPreview(), loadReconciliationResults()])
  } catch (error) {
    state.message = `上传失败：${error?.response?.data?.detail || error.message}`
  } finally {
    state.loading = false
  }
}

const loadPreview = async () => {
  if (!state.previewBatchId) return
  try {
    const { data } = await axios.get(`/api/imports/${state.previewBatchId}/preview`)
    state.previewRows = data
  } catch (error) {
    state.message = `预览失败：${error?.response?.data?.detail || error.message}`
  }
}

const runReconciliation = async () => {
  if (!state.reconciliationForm.statement_batch_id || !state.reconciliationForm.inbound_batch_id) {
    return (state.message = '请选择对账单批次和入库单批次')
  }
  state.loading = true
  try {
    await axios.post('/api/reconciliation/run', null, {
      params: {
        statement_batch_id: state.reconciliationForm.statement_batch_id,
        inbound_batch_id: state.reconciliationForm.inbound_batch_id
      }
    })
    state.message = '对账任务已执行'
    await Promise.all([loadSummary(), loadPurchases(), loadReconciliationResults()])
  } catch (error) {
    state.message = `执行对账失败：${error?.response?.data?.detail || error.message}`
  } finally {
    state.loading = false
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

const deleteBatch = async (batchId) => {
  state.loading = true
  try {
    await axios.delete(`/api/imports/${batchId}`)
    state.message = `已删除批次 #${batchId}`
    await loadAll()
    if (String(batchId) === state.previewBatchId) state.previewRows = []
  } catch (error) {
    state.message = `删除批次失败：${error?.response?.data?.detail || error.message}`
  } finally {
    state.loading = false
  }
}

export function useAppData () {
  return {
    state,
    statusOptions,
    reconOptions,
    loadAll,
    onFileChange,
    uploadFile,
    loadPreview,
    runReconciliation,
    loadReconciliationResults,
    updateInvoice,
    updateReconciliation,
    removePurchase,
    deleteBatch
  }
}
