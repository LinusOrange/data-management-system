<template>
  <section class="panel">
    <h2>文件与已解析条目管理</h2>
    <h3>全部文件批次</h3>
    <table>
      <thead><tr><th>批次ID</th><th>来源</th><th>文件</th><th>上传时间</th><th>解析状态</th><th>失败原因</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="b in state.batches" :key="b.id">
          <td>#{{ b.id }}</td><td>{{ b.source_type }}</td><td>{{ b.file_name }}</td><td>{{ b.uploaded_at }}</td><td>{{ b.parse_status }}</td><td>{{ b.parse_error || '-' }}</td>
          <td><button class="danger-btn" @click="deleteBatch(b.id)">删除批次</button></td>
        </tr>
      </tbody>
    </table>

    <h3>入库单已解析条目</h3>
    <table>
      <thead><tr><th>批次</th><th>行号</th><th>名称</th><th>货号</th><th>数量</th><th>金额</th><th>订单号</th></tr></thead>
      <tbody>
        <tr v-for="row in state.managedInboundRows" :key="`in-${row.id}`">
          <td>#{{ row.batch_id }}</td><td>{{ row.row_no }}</td><td>{{ row.name || '-' }}</td><td>{{ row.item_code || '-' }}</td><td>{{ row.qty || '-' }}</td><td>{{ row.amount || '-' }}</td><td>{{ row.order_no || '-' }}</td>
        </tr>
      </tbody>
    </table>

    <h3>对账单已解析条目</h3>
    <table>
      <thead><tr><th>批次</th><th>行号</th><th>名称</th><th>货号</th><th>数量</th><th>金额</th><th>订单号</th></tr></thead>
      <tbody>
        <tr v-for="row in state.managedStatementRows" :key="`st-${row.id}`">
          <td>#{{ row.batch_id }}</td><td>{{ row.row_no }}</td><td>{{ row.name || '-' }}</td><td>{{ row.item_code || '-' }}</td><td>{{ row.qty || '-' }}</td><td>{{ row.amount || '-' }}</td><td>{{ row.order_no || '-' }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { useAppData } from '../composables/useAppData'
const { state, deleteBatch } = useAppData()
</script>
