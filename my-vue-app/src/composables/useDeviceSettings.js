import { ref, watch } from 'vue';

export const useDeviceSettings = () => {
  const deviceToken = ref(localStorage.getItem('tablet_device_token') || '');
  const deviceId = ref(localStorage.getItem('tablet_device_id') || 'tablet-01');

  watch(deviceToken, (value) => {
    localStorage.setItem('tablet_device_token', value || '');
  });

  watch(deviceId, (value) => {
    localStorage.setItem('tablet_device_id', value || '');
  });

  return { deviceToken, deviceId };
};

export const buildHeaders = (token, extra = {}) => {
  const headers = { ...extra };
  if (token) headers['X-Device-Token'] = token;
  return headers;
};
