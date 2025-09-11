<template>
  <span class="tag-chip" :class="{ clickable: clickable }" @click="handleClick">
    {{ tag }}
  </span>
</template>

<script>
export default {
  name: 'TagChip',
  props: {
    tag: {
      type: String,
      required: true
    },
    clickable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click'],
  methods: {
    handleClick() {
      if (this.clickable) {
        this.$emit('click', this.tag)
      }
    }
  }
}
</script>

<style scoped>
.tag-chip {
  display: inline-block;
  background: #e2e8f0;
  color: #475569;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  margin: 0.125rem;
  border: 1px solid #cbd5e1;
}

.tag-chip.clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-chip.clickable:hover {
  background: #cbd5e1;
  color: #334155;
  border-color: #94a3b8;
  transform: translateY(-1px);
}
</style>
