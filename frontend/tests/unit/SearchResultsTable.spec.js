import { mount } from '@vue/test-utils';
import SearchResultsTable from '@/components/search/SearchResultsTable.vue';

const sampleProducts = [
  {
    id: 1,
    artid: '123',
    brand: 'BrandA',
    name: 'Item A',
    source: 'Armtek',
    details_status: 'ready'
  },
  {
    id: 2,
    artid: '456',
    brand: 'BrandB',
    name: 'Item B',
    source: 'Armtek',
    details_status: 'pending'
  }
];

describe('SearchResultsTable', () => {
  it('renders rows for products and statuses', () => {
    const wrapper = mount(SearchResultsTable, {
      props: { products: sampleProducts }
    });

    const rows = wrapper.findAll('tbody tr');
    expect(rows).toHaveLength(2);
    expect(rows[0].text()).toContain('123');
    expect(rows[1].text()).toContain('ожидание');
  });

  it('emits request-details and refresh', async () => {
    const wrapper = mount(SearchResultsTable, {
      props: { products: sampleProducts }
    });

    await wrapper.get('button.btn-outline-gradient').trigger('click');
    await wrapper.get('button.btn-outline-light').trigger('click');

    expect(wrapper.emitted()['request-details']).toBeTruthy();
    expect(wrapper.emitted().refresh).toBeTruthy();
  });
});
