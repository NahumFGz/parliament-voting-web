import type { VotacionItem } from '../../../workers/useSearchWorker'
import { formatDate } from '../utils/formatDate'

interface VotacionesListProps {
  results: VotacionItem[]
  displayLimit: number
  hasFilters: boolean
  onLoadMore: () => void
  onViewPdf: (item: VotacionItem) => void
}

export function VotacionesList({
  results,
  displayLimit,
  hasFilters,
  onLoadMore,
  onViewPdf
}: VotacionesListProps) {
  if (results.length === 0) {
    return (
      <div className='py-10 text-center bg-amber-50 rounded-lg border border-amber-300'>
        <p className='m-0'>No se encontraron resultados con los filtros seleccionados.</p>
      </div>
    )
  }

  return (
    <div>
      <div className='mb-4 flex justify-between items-center'>
        <h2 className='m-0 text-2xl font-bold'>
          {hasFilters
            ? `Resultados: ${results.length.toLocaleString()} votaciones`
            : `Votaciones más recientes`}
        </h2>
        {results.length > displayLimit && (
          <span className='text-sm text-gray-600'>
            Mostrando {displayLimit} de {results.length.toLocaleString()}
          </span>
        )}
      </div>

      <div className='flex flex-col gap-4'>
        {results.slice(0, displayLimit).map((item) => (
          <div key={item.id} className='p-4 bg-white border border-gray-300 rounded-lg shadow-sm'>
            <div className='flex justify-between items-start mb-2.5'>
              <div className='flex-1'>
                <div className='text-sm text-gray-600 mb-2'>📅 {formatDate(item.fecha_hora)}</div>
                <p className='m-0 leading-relaxed'>{item.asunto}</p>
              </div>
            </div>
            <div className='flex justify-between items-center mt-2.5 pt-2.5 border-t border-gray-200'>
              <span className='text-xs text-gray-500'>Página: {item.pagina}</span>
              <button
                onClick={() => onViewPdf(item)}
                className='px-3 py-1.5 bg-green-500 text-white no-underline rounded text-sm font-bold hover:bg-green-600 transition-colors cursor-pointer border-none'
              >
                Ver Votaciones
              </button>
            </div>
          </div>
        ))}

        {results.length > displayLimit && (
          <div className='text-center mt-5'>
            <button
              onClick={onLoadMore}
              className='px-8 py-3 text-base font-bold bg-green-500 text-white border-none rounded cursor-pointer hover:bg-green-600 transition-colors'
            >
              Cargar más resultados ({results.length - displayLimit} restantes)
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
