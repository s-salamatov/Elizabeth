import { mount } from '@vue/test-utils';
import AlertMessage from '../AlertMessage.vue';

describe('AlertMessage', () => {
  it('renders the provided message', () => {
    const wrapper = mount(AlertMessage, {
      props: {
        message: 'Test message',
        variant: 'success',
      },
    });

    expect(wrapper.text()).toContain('Test message');
    expect(wrapper.find('i').classes()).toContain('bi-check-circle-fill');
  });

  it('uses info icon by default', () => {
    const wrapper = mount(AlertMessage, {
      props: { message: 'Information' },
    });

    expect(wrapper.find('i').classes()).toContain('bi-info-circle-fill');
  });
});
