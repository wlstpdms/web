import { apiBaseUrl } from './index.js'

export function startKakaoAuth() {
  window.location.assign(`${apiBaseUrl}/api/user/kakao/authorize`)
}
