import { PdfViewerModal, SearchFilters, VotacionesList } from '../components'
import { useEncabezadosFechas, useVotacionesSearch, usePdfModal } from '../hooks'
import { formatDate } from '../utils/formatDate'

export function HomePage() {
  // Hook para manejar la búsqueda y resultados
  const {
    isLoading,
    dataCount,
    error,
    results,
    isSearching,
    hasSearched,
    displayLimit,
    filters,
    setAsunto,
    setFechaDesde,
    setFechaHasta,
    handleSearch,
    clearFilters,
    loadMore
  } = useVotacionesSearch()

  const { oldestDate, latestDate } = useEncabezadosFechas()
  const hasDateRange = !!(oldestDate && latestDate)

  // Hook para manejar el modal de PDF
  const { selectedPdf, openModal, closeModal } = usePdfModal()

  // Verificar si hay filtros activos
  const hasFilters = !!(filters.asunto || filters.fechaDesde || filters.fechaHasta)

  if (error) {
    return (
      <div className='py-5'>
        <div className='p-5 bg-red-50 border border-red-200 rounded-lg'>
          <h2>Error al cargar datos</h2>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className='py-5'>
      {isLoading ? (
        <div className='py-10 text-center bg-gray-100 rounded-lg'>
          <p className='text-lg'>Cargando datos...</p>
        </div>
      ) : (
        <>
          <div className='mb-5 p-4 bg-green-50 rounded-lg border border-green-500 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between sm:gap-4'>
            <p className='m-0 font-bold min-w-0'>
              ✓ {dataCount.toLocaleString()} votaciones cargadas
            </p>
            {hasDateRange && (
              <div className='text-sm text-green-700 space-y-1 self-start sm:self-auto text-left sm:text-right shrink-0 sm:max-w-[min(100%,22rem)]'>
                <p className='m-0 tabular-nums'>
                  <span className='text-green-800/80'>Votación más reciente:</span>{' '}
                  {formatDate(latestDate)}
                </p>
                <p className='m-0 tabular-nums'>
                  <span className='text-green-800/80'>Votación más antigua:</span>{' '}
                  {formatDate(oldestDate)}
                </p>
              </div>
            )}
          </div>

          <SearchFilters
            asunto={filters.asunto}
            fechaDesde={filters.fechaDesde}
            fechaHasta={filters.fechaHasta}
            isLoading={isLoading}
            isSearching={isSearching}
            hasActiveFilters={hasFilters}
            onAsuntoChange={setAsunto}
            onFechaDesdeChange={setFechaDesde}
            onFechaHastaChange={setFechaHasta}
            onSearch={handleSearch}
            onClear={clearFilters}
          />

          {hasSearched && (
            <VotacionesList
              results={results}
              displayLimit={displayLimit}
              hasFilters={hasFilters}
              onLoadMore={loadMore}
              onViewPdf={openModal}
            />
          )}
        </>
      )}

      <PdfViewerModal selectedPdf={selectedPdf} onClose={closeModal} />
    </div>
  )
}
