<template>
  <section>
    <div class="kpis">
      <article class="card warn"><h3>未对账</h3><p>{{ state.summary.pending_reconciliation_count }}</p></article>
      <article class="card warn"><h3>未开票</h3><p>{{ state.summary.pending_invoice_count }}</p></article>
      <article class="card danger"><h3>异常</h3><p>{{ state.summary.reconciliation_exception_count }}</p></article>
      <article class="card ok"><h3>已闭环</h3><p>{{ state.summary.closed_loop_count }}</p></article>
    </div>
  </section>
</template>

<script setup>
import { useAppData } from '../composables/useAppData'
const { state } = useAppData()
</script>
