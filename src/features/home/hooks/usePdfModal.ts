import { useState, useCallback } from 'react'
import type { VotacionItem } from '../../../workers/useSearchWorker'

export function usePdfModal() {
  const [selectedPdf, setSelectedPdf] = useState<VotacionItem | null>(null)

  const openModal = useCallback((item: VotacionItem) => {
    setSelectedPdf(item)
  }, [])

  const closeModal = useCallback(() => {
    setSelectedPdf(null)
  }, [])

  return {
    selectedPdf,
    openModal,
    closeModal
  }
}

