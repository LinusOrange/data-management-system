<template>
  <section class="panel">
    <h2>对账页面</h2>
    <p>规则：货号+订单号相同后，数量与金额都一致为成功；未匹配或数量金额不一致为失败。</p>

    <div class="form-grid">
      <label>对账单批次
        <select v-model="state.reconciliationForm.statement_batch_id" @change="loadReconciliationResults">
          <option value="">请选择</option>
          <option v-for="b in state.batches.filter(x => x.source_type === 'statement')" :key="b.id" :value="b.id">#{{ b.id }}</option>
        </select>
      </label>
      <label>入库单批次
        <select v-model="state.reconciliationForm.inbound_batch_id" @change="loadReconciliationResults">
          <option value="">请选择</option>
          <option v-for="b in state.batches.filter(x => x.source_type === 'inbound')" :key="b.id" :value="b.id">#{{ b.id }}</option>
        </select>
      </label>
    </div>
    <button class="primary" :disabled="state.loading" @click="runReconciliation">执行所选批次对账</button>

    <h3>已完成对账条目（成功）</h3>
    <table>
      <thead><tr><th>订单号</th><th>货号</th><th>对账单数量</th><th>入库单数量</th><th>对账单金额</th><th>入库单金额</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.success" :key="`ok-${row.match_key}`">
          <td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.inbound_qty_sum || '-' }}</td>
          <td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td>
        </tr>
      </tbody>
    </table>

    <h3>未完成对账（数量或金额不一致）</h3>
    <table>
      <thead><tr><th>订单号</th><th>货号</th><th>对账单数量</th><th>入库单数量</th><th>对账单金额</th><th>入库单金额</th><th>失败类型</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed_diff" :key="`diff-${row.match_key}`">
          <td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.inbound_qty_sum || '-' }}</td>
          <td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td>
          <td>{{ row.match_status }}</td>
        </tr>
      </tbody>
    </table>

    <h3>未匹配对账单条目（仅对账单池）</h3>
    <table>
      <thead><tr><th>订单号</th><th>货号</th><th>对账单数量</th><th>对账单金额</th><th>失败类型</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed_statement_only" :key="`stmt-${row.match_key}`">
          <td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.statement_amt_sum || '-' }}</td>
          <td>{{ row.match_status }}</td>
        </tr>
      </tbody>
    </table>

    <h3>未匹配入库单条目（仅入库单池）</h3>
    <table>
      <thead><tr><th>订单号</th><th>货号</th><th>入库单数量</th><th>入库单金额</th><th>失败类型</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed_inbound_only" :key="`inb-${row.match_key}`">
          <td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.inbound_qty_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td>
          <td>{{ row.match_status }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { useAppData } from '../composables/useAppData'
const { state, runReconciliation, loadReconciliationResults } = useAppData()
</script>
