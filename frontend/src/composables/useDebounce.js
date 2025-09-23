import { ref, watch } from 'vue';

export function useDebounce(sourceRef, delay = 500) {
  const debounced = ref(sourceRef.value);
  let timer = null;

  watch(sourceRef, (newVal) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      debounced.value = newVal;
    }, delay);
  });

  return debounced;
}
