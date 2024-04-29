import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => {
  let base = './'
  // 根据命令模式动态设置base
  if (command === 'build') {
    base = 'static/'
  }
  return {
    base,
    plugins: [react()]
  }
})
