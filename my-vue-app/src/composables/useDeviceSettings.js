import { computed, ref, watch } from 'vue'

const TOKEN_KEY = 'device_token'
const DEVICE_ID_KEY = 'device_id'

export function useDeviceSettings() {
  const deviceToken = ref(localStorage.getItem(TOKEN_KEY) || '')
  const deviceId = ref(localStorage.getItem(DEVICE_ID_KEY) || '')

  watch(deviceToken, (val) => {
    if (val) {
      localStorage.setItem(TOKEN_KEY, val)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  })

  watch(deviceId, (val) => {
    if (val) {
      localStorage.setItem(DEVICE_ID_KEY, val)
    } else {
      localStorage.removeItem(DEVICE_ID_KEY)
    }
  })

  const hasAuth = computed(() => Boolean(deviceToken.value))

  const reset = () => {
    deviceToken.value = ''
    deviceId.value = ''
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(DEVICE_ID_KEY)
  }

  return {
    deviceToken,
    deviceId,
    hasAuth,
    reset,
  }
}
