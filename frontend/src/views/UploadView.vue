<template>
  <section class="panel">
    <h2>上传文件并自动解析</h2>
    <div class="form-grid">
      <label>文件类型
        <select v-model="state.uploadForm.source_type">
          <option value="statement">对账单（statement）</option>
          <option value="inbound">入库单（inbound）</option>
        </select>
      </label>
      <label>上传人
        <input v-model="state.uploadForm.uploaded_by" placeholder="可选" />
      </label>
      <label class="full">选择文件<input type="file" @change="onFileChange" /></label>
    </div>
    <button class="primary" :disabled="state.loading" @click="uploadFile">上传并解析</button>

    <hr />
    <h3>数据预览（名称 / 货号 / 数量 / 金额 / 订单号）</h3>
    <div class="panel-head">
      <select v-model="state.previewBatchId">
        <option value="">选择批次</option>
        <option v-for="b in state.batches" :key="b.id" :value="String(b.id)">#{{ b.id }} - {{ b.source_type }}</option>
      </select>
      <button class="refresh" @click="loadPreview">加载预览</button>
    </div>
    <table>
      <thead>
        <tr><th>名称</th><th>货号</th><th>数量</th><th>金额</th><th>订单号</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in state.previewRows" :key="`${row.row_no}-${row.order_no || ''}`">
          <td>{{ row.name || '-' }}</td><td>{{ row.item_code || '-' }}</td><td>{{ row.qty || '-' }}</td><td>{{ row.amount || '-' }}</td><td>{{ row.order_no || '-' }}</td>
        </tr>
      </tbody>
    </table>

  </section>
</template>

<script setup>
import { useAppData } from '../composables/useAppData'
const { state, onFileChange, uploadFile, loadPreview } = useAppData()
</script>
