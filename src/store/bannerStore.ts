import { create } from 'zustand'
import { devtools, persist, createJSONStorage } from 'zustand/middleware'

interface BannerStore {
  isVisible: boolean
  toggleBanner: () => void
  hideBanner: () => void
  showBanner: () => void
}

export const useBannerStore = create<BannerStore>()(
  devtools(
    persist(
      (set) => ({
        isVisible: true,
        toggleBanner: () =>
          set((state) => ({
            isVisible: !state.isVisible
          })),
        hideBanner: () =>
          set(() => ({
            isVisible: false
          })),
        showBanner: () =>
          set(() => ({
            isVisible: true
          }))
      }),
      {
        name: 'banner-storage',
        storage: createJSONStorage(() => sessionStorage),
        partialize: (state) =>
          ({
            isVisible: state.isVisible
          } satisfies Partial<BannerStore>)
      }
    )
  )
)

export function useBannerStoreDispatch() {
  const isVisible = useBannerStore((state) => state.isVisible)
  const toggleBanner = useBannerStore((state) => state.toggleBanner)
  const hideBanner = useBannerStore((state) => state.hideBanner)
  const showBanner = useBannerStore((state) => state.showBanner)

  return { isVisible, toggleBanner, hideBanner, showBanner }
}
