import { defineStore } from 'pinia';

export const useWebGPUStore = defineStore('webgpu', {
  state: () => ({
    isSupported: true as boolean,
  }),
  actions: {
    setSupport(value: boolean) {
      this.isSupported = value;
    }
  }
});
