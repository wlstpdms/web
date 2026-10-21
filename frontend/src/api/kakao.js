import { apiUrl } from './config.js'

export function startKakaoAuth() {
  window.location.assign(apiUrl('/user/kakao/authorize'))
}
