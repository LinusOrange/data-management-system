<template>
  <section class="panel">
    <h2>对账页面</h2>
    <p>规则：货号+订单号相同后，数量与金额都一致为成功；未匹配或数量金额不一致为失败。</p>

    <h3>已完成对账条目（成功）</h3>
    <table>
      <thead><tr><th>订单号</th><th>货号</th><th>对账单数量</th><th>入库单数量</th><th>对账单金额</th><th>入库单金额</th><th>状态</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.success" :key="`ok-${row.match_key}`">
          <td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.inbound_qty_sum || '-' }}</td>
          <td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td>
          <td>成功</td>
        </tr>
      </tbody>
    </table>

    <h3>未完成对账条目（失败）</h3>
    <table>
      <thead><tr><th>订单号</th><th>货号</th><th>对账单数量</th><th>入库单数量</th><th>对账单金额</th><th>入库单金额</th><th>失败类型</th></tr></thead>
      <tbody>
        <tr v-for="row in state.reconciliationResults.failed" :key="`fail-${row.match_key}`">
          <td>{{ row.order_no || '-' }}</td><td>{{ row.item_code || '-' }}</td>
          <td>{{ row.statement_qty_sum || '-' }}</td><td>{{ row.inbound_qty_sum || '-' }}</td>
          <td>{{ row.statement_amt_sum || '-' }}</td><td>{{ row.inbound_amt_sum || '-' }}</td>
          <td>{{ row.match_status }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { useAppData } from '../composables/useAppData'
const { state } = useAppData()
</script>
