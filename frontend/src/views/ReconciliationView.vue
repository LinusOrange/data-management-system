<template>
  <section class="panel glass-panel">
    <div class="section-head">
      <div>
        <h2>对账页面</h2>
        <p class="subtle">规则：先按 货号 + 订单号 匹配；匹配后数量和金额都一致才算成功。</p>
      </div>
      <button class="primary" :disabled="state.loading" @click="runReconciliation">执行所选文件对账</button>
    </div>

    <div class="form-grid">
      <label>对账单文件
        <select v-model="state.reconciliationForm.statement_file_name" @change="loadReconciliationResults">
          <option value="">请选择</option>
          <option v-for="b in state.batches.filter(x => x.source_type === 'statement')" :key="b.id" :value="b.file_name">{{ (b.file_name || '').split('/').pop() }}</option>
        </select>
      </label>
      <label>入库单文件
        <select v-model="state.reconciliationForm.inbound_file_name" @change="loadReconciliationResults">
          <option value="">请选择</option>
          <option v-for="b in state.batches.filter(x => x.source_type === 'inbound')" :key="b.id" :value="b.file_name">{{ (b.file_name || '').split('/').pop() }}</option>
        </select>
      </label>
    </div>

    <div class="kpis recon-kpis">
      <article class="card ok"><h3>对账成功</h3><p>{{ state.reconciliationResults.success.length }}</p></article>
      <article class="card danger"><h3>数量/金额不符</h3><p>{{ state.reconciliationResults.failed_diff.length }}</p></article>
      <article class="card warn"><h3>仅对账单</h3><p>{{ state.reconciliationResults.failed_statement_only.length }}</p></article>
      <article class="card warn"><h3>仅入库单</h3><p>{{ state.reconciliationResults.failed_inbound_only.length }}</p></article>
    </div>

    <h3>已完成对账条目（成功）</h3>
    <table>
      <thead><tr><th>名称</th><th>订单号</th><th>货号</th><th>对账单数量</th><th>入库单数量</th><th>对账单金额</th><th>入库单金额</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.success" :key="`ok-${row.match_key}`">
          <td>{{ row.item_name || '-' }}</td><td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.inbound_qty_sum || '-' }}</td>
          <td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td>
        </tr>
      </tbody>
    </table>

    <h3>金额/数量不符条目（货号+订单号已匹配）</h3>
    <table>
      <thead><tr><th>名称</th><th>订单号</th><th>货号</th><th>对账单数量</th><th>入库单数量</th><th>数量差</th><th>对账单金额</th><th>入库单金额</th><th>金额差</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed_diff" :key="`diff-${row.match_key}`">
          <td>{{ row.item_name || '-' }}</td><td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.inbound_qty_sum || '-' }}</td><td>{{ row.qty_diff || '-' }}</td>
          <td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td><td>{{ row.amt_diff || '-' }}</td>
        </tr>
      </tbody>
    </table>

    <h3>未匹配对账单条目（仅对账单池）</h3>
    <table>
      <thead><tr><th>名称</th><th>订单号</th><th>货号</th><th>对账单数量</th><th>对账单金额</th><th>失败类型</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed_statement_only" :key="`stmt-${row.match_key}`">
          <td>{{ row.item_name || '-' }}</td><td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.match_status }}</td>
        </tr>
      </tbody>
    </table>

    <h3>未匹配入库单条目（仅入库单池）</h3>
    <table>
      <thead><tr><th>名称</th><th>订单号</th><th>货号</th><th>入库单数量</th><th>入库单金额</th><th>失败类型</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed_inbound_only" :key="`inb-${row.match_key}`">
          <td>{{ row.item_name || '-' }}</td><td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.inbound_qty_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td><td>{{ row.match_status }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { useAppData } from '../composables/useAppData'
const { state, runReconciliation, loadReconciliationResults } = useAppData()
</script>
