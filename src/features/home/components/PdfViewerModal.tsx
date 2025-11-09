import { useEffect } from 'react'
import type { VotacionItem } from '../../../workers/useSearchWorker'

interface PdfViewerModalProps {
  selectedPdf: VotacionItem | null
  onClose: () => void
}

export function PdfViewerModal({ selectedPdf, onClose }: PdfViewerModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && selectedPdf) {
        onClose()
      }
    }

    if (selectedPdf) {
      document.addEventListener('keydown', handleEscape)
      // Prevenir scroll del body cuando el modal está abierto
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [selectedPdf, onClose])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('es-PE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!selectedPdf) return null

  return (
    <div
      className='fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200'
      onClick={onClose}
    >
      <div
        className='bg-white rounded-lg shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col animate-in zoom-in-95 duration-200'
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header del modal */}
        <div className='flex justify-between items-start p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-white'>
          <div className='flex-1 pr-4'>
            <h3 className='text-lg font-bold mb-2 text-gray-800'>Documento de Votación</h3>
            <p className='text-sm text-gray-600 mb-1'>📅 {formatDate(selectedPdf.fecha_hora)}</p>
            <p className='text-xs text-gray-500 line-clamp-2'>{selectedPdf.asunto}</p>
          </div>
          <button
            onClick={onClose}
            className='text-gray-500 hover:text-gray-700 text-3xl font-bold leading-none px-3 py-1 hover:bg-gray-100 rounded transition-colors'
            aria-label='Cerrar modal'
          >
            ×
          </button>
        </div>

        {/* Visor de PDF */}
        <div className='flex-1 overflow-hidden relative bg-gray-100'>
          <iframe
            src={selectedPdf.url}
            className='w-full h-full border-none'
            title='Visor de PDF'
          />
        </div>

        {/* Footer del modal */}
        <div className='flex justify-between items-center p-4 border-t border-gray-200 bg-gray-50'>
          <span className='text-sm text-gray-600'>Página: {selectedPdf.pagina}</span>
          <div className='flex gap-2'>
            <button
              onClick={onClose}
              className='px-4 py-2 text-sm font-semibold bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors'
            >
              Cerrar
            </button>
            <a
              href={selectedPdf.url}
              target='_blank'
              rel='noopener noreferrer'
              className='px-4 py-2 text-sm font-semibold bg-blue-500 text-white no-underline rounded hover:bg-blue-600 transition-colors inline-flex items-center gap-2'
            >
              <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={2}
                  d='M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14'
                />
              </svg>
              Ver documento oficial
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

