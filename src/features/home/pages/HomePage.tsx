import { PdfViewerModal, SearchFilters, VotacionesList } from '../components'
import { useVotacionesSearch, usePdfModal } from '../hooks'
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
    latestDate,
    filters,
    setAsunto,
    setFechaDesde,
    setFechaHasta,
    handleSearch,
    clearFilters,
    loadMore
  } = useVotacionesSearch()

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
          <div className='mb-5 p-4 bg-green-50 rounded-lg border border-green-500'>
            <p className={`m-0 font-bold ${latestDate ? 'mb-2' : ''}`}>
              ✓ {dataCount.toLocaleString()} votaciones cargadas
            </p>
            {latestDate && (
              <p className='m-0 text-sm text-green-700'>
                📅 Última votación registrada: {formatDate(latestDate)}
              </p>
            )}
          </div>

          <SearchFilters
            asunto={filters.asunto}
            fechaDesde={filters.fechaDesde}
            fechaHasta={filters.fechaHasta}
            isLoading={isLoading}
            isSearching={isSearching}
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
