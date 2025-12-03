<template>
  <div class="card table-card">
    <div class="card-body">
      <div class="section-card-title mb-3">
        <div>
          <h5 class="card-title mb-1">Результаты поиска</h5>
          <p class="text-muted mb-0">
            <span v-if="products.length">Найдено {{ products.length }} товаров. Получите характеристики, чтобы увидеть фото, цену и наличие.</span>
            <span v-else>Результатов пока нет. Введите артикулы и нажмите «Найти».</span>
          </p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-outline-gradient" :disabled="products.length === 0 || requesting" @click="requestDetails">
            <span v-if="requesting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <i v-else class="bi bi-collection-play me-1"></i>
            {{ requesting ? 'Идёт обработка…' : 'Получить характеристики товаров' }}
          </button>
          <button class="btn btn-ghost btn-outline-light" :disabled="refreshing" @click="$emit('refresh')">
            <i class="bi bi-arrow-repeat me-1"></i> Обновить
          </button>
        </div>
      </div>
      <div v-if="products.length === 0" class="empty-state">
        Результатов пока нет. Введите артикулы и нажмите «Найти».
      </div>
      <div v-else>
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Артикул</th>
                <th>Бренд</th>
                <th>Наименование</th>
                <th>Цена</th>
                <th>Наличие</th>
                <th>Доставка</th>
                <th>Статус характеристик</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <template v-for="product in products" :key="product.id">
                <tr>
                  <td class="fw-semibold">{{ product.artid }}</td>
                  <td>{{ product.brand }}</td>
                  <td>{{ product.name }}</td>
                  <td>{{ formatPrice(product) }}</td>
                  <td>
                    <span class="badge-pill muted-chip text-uppercase">{{ formatAvailability(product) }}</span>
                  </td>
                  <td>{{ formatDelivery(product) }}</td>
                  <td>
                    <span
                      :class="statusClass(product.details_status)"
                      :title="tooltipText(product.details_status)"
                    >
                      <i :class="statusIcon(product.details_status)" class="me-1"></i>
                      {{ statusLabel(product.details_status) }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button class="btn btn-ghost btn-sm" type="button" @click="toggle(product.id)">
                      <i :class="expanded.has(product.id) ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="expanded.has(product.id)" :key="`${product.id}-details`">
                  <td colspan="8" class="bg-body-tertiary">
                    <div class="detail-grid">
                      <div
                        v-for="entry in detailEntries(product)"
                        :key="entry.label"
                        class="detail-chip"
                      >
                        <span class="detail-label">{{ entry.label }}</span>
                        <span class="detail-value">{{ entry.value }}</span>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <div class="table-help mt-2">
          <i class="bi bi-arrows-expand"></i>
          <span>На мобильных таблица скроллится по горизонтали.</span>
        </div>
      </div>
      <AlertMessage
        v-if="helperMessage"
        :message="helperMessage"
        variant="info"
        class="mt-3"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AlertMessage from '../common/AlertMessage.vue';

defineProps({
  products: { type: Array, default: () => [] },
  requesting: { type: Boolean, default: false },
  refreshing: { type: Boolean, default: false },
  helperMessage: { type: String, default: '' },
});

const emit = defineEmits(['request-details', 'refresh']);

const expanded = ref(new Set());

const toggle = (id) => {
  const next = new Set(expanded.value);
  next.has(id) ? next.delete(id) : next.add(id);
  expanded.value = next;
};

const detailEntries = (product) => {
  const mapping = [
    ['Код склада партнёра', product.warehouse_partner],
    ['Код склада Armtek', product.warehouse_code],
    ['Доступное количество', product.available_quantity],
    ['Дней на возврат', product.return_days],
    ['Кратность заказа', product.multiplicity],
    ['Минимальная партия', product.minimum_order],
    ['Вероятность поставки', formatProbability(product.supply_probability)],
    ['Дата поставки', product.delivery_date],
    ['Дата гарантии', product.warranty_date],
    ['Признак Импорт/ПРО', product.import_flag],
    ['Признак 713', product.special_flag],
    ['Максимальная розн. цена', formatMoney(product.max_retail_price, product.currency)],
    ['Наценка', formatMoney(product.markup, product.currency)],
    ['Надбавка импортёра', formatMoney(product.importer_markup, product.currency)],
    ['Отпускная цена производителя', formatMoney(product.producer_price, product.currency)],
    ['Остаток надбавки (₽)', formatMoney(product.markup_rest_rub, product.currency)],
    ['Остаток надбавки (%)', formatPercent(product.markup_rest_percent)],
    ['Аналог', product.is_analog === null ? '—' : product.is_analog ? 'Да' : 'Нет'],
    ['Примечание', product.note],
  ];
  return mapping.filter(([, value]) => value !== null && value !== undefined && value !== '');
};

const statusClass = (status) => {
  switch (status) {
    case 'ready':
      return 'status-pill ready';
    case 'failed':
      return 'status-pill failed';
    case 'pending':
      return 'status-pill pending';
    default:
      return 'status-pill idle';
  }
};

const statusIcon = (status) => {
  switch (status) {
    case 'ready':
      return 'bi bi-check-circle-fill';
    case 'failed':
      return 'bi bi-exclamation-octagon-fill';
    default:
      return 'bi bi-arrow-repeat';
  }
};

const statusLabel = (status) => {
  switch (status) {
    case 'ready':
      return 'получены';
    case 'failed':
      return 'ошибка';
    default:
      return 'ожидание';
  }
};

const tooltipText = (status) => {
  switch (status) {
    case 'ready':
      return 'Характеристики получены через расширение';
    case 'failed':
      return 'Ошибка при получении характеристик';
    default:
      return 'В очереди или в процессе получения';
  }
};

const requestDetails = () => emit('request-details');

const formatPrice = (product) => {
  if (product.price === null || product.price === undefined) return '—';
  const currency = product.currency || '';
  return `${product.price} ${currency}`.trim();
};

const formatAvailability = (product) => {
  const qty = product.available_quantity ?? '—';
  const warehouse = product.warehouse_code || product.warehouse_partner || '';
  const multiplicity = product.multiplicity ? ` x${product.multiplicity}` : '';
  return `${qty}${multiplicity}${warehouse ? ` • ${warehouse}` : ''}`.trim();
};

const formatDelivery = (product) => {
  if (product.delivery_date) return product.delivery_date;
  if (product.return_days !== null && product.return_days !== undefined)
    return `${product.return_days} дн. на возврат`;
  return '—';
};

const formatProbability = (value) => {
  if (value === null || value === undefined) return null;
  return `${value}%`;
};

const formatMoney = (value, currency = '') => {
  if (value === null || value === undefined) return null;
  return `${value} ${currency}`.trim();
};

const formatPercent = (value) => {
  if (value === null || value === undefined) return null;
  return `${value}%`;
};
</script>

<style scoped>
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  padding: 12px 8px;
}

.detail-chip {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  border: 1px solid #dfe3f0;
  border-radius: 12px;
  padding: 10px 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.detail-label {
  display: block;
  font-size: 12px;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-value {
  display: block;
  font-weight: 600;
  color: #1f2937;
}
</style>
