import { mount } from '@vue/test-utils';
import SearchForm from '../SearchForm.vue';

describe('SearchForm', () => {
  it('synchronizes textarea value with modelValue prop', async () => {
    const wrapper = mount(SearchForm, {
      props: {
        modelValue: 'initial query',
      },
    });

    const textarea = wrapper.get('textarea');
    expect(textarea.element.value).toBe('initial query');

    await wrapper.setProps({ modelValue: 'updated query' });
    expect(textarea.element.value).toBe('updated query');
  });

  it('emits update and submit events when searching', async () => {
    const wrapper = mount(SearchForm, {
      props: {
        modelValue: '',
      },
    });

    const textarea = wrapper.get('textarea');
    await textarea.setValue('KYB 332101');

    expect(wrapper.emitted()['update:modelValue'][0]).toEqual(['KYB 332101']);

    await wrapper.get('button.btn-gradient').trigger('click');

    const submitEvents = wrapper.emitted('submit');
    expect(submitEvents).toBeTruthy();
    expect(submitEvents[0][0]).toEqual({ value: 'KYB 332101', preserve: true });
  });

  it('clears the field when reset is clicked', async () => {
    const wrapper = mount(SearchForm, {
      props: {
        modelValue: 'value to clear',
      },
    });

    await wrapper.get('button.btn-ghost').trigger('click');

    expect(wrapper.emitted()['update:modelValue'].at(-1)).toEqual(['']);
    expect(wrapper.get('textarea').element.value).toBe('');
  });
});
