interface SearchFiltersProps {
  asunto: string
  fechaDesde: string
  fechaHasta: string
  isLoading: boolean
  isSearching: boolean
  hasActiveFilters: boolean
  onAsuntoChange: (value: string) => void
  onFechaDesdeChange: (value: string) => void
  onFechaHastaChange: (value: string) => void
  onSearch: () => void
  onClear: () => void
}

export function SearchFilters({
  asunto,
  fechaDesde,
  fechaHasta,
  isLoading,
  isSearching,
  hasActiveFilters,
  onAsuntoChange,
  onFechaDesdeChange,
  onFechaHastaChange,
  onSearch,
  onClear
}: SearchFiltersProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isSearching && !isLoading) {
      onSearch()
    }
  }

  return (
    <div className='mb-8 p-5 bg-gray-50 rounded-lg border border-gray-300'>
      <h2 className='mt-0 mb-5 text-2xl font-bold'>Filtros de Búsqueda</h2>

      <div className='mb-4'>
        <label className='block mb-1 font-bold'>Buscar por Asunto:</label>
        <input
          type='text'
          value={asunto}
          onChange={(e) => onAsuntoChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder='Ejemplo: presupuesto, ley, investigadora... (Enter para buscar)'
          className='w-full p-2.5 text-base rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed'
          disabled={isLoading}
        />
      </div>

      <div className='grid grid-cols-2 gap-4 mb-4'>
        <div>
          <label className='block mb-1 font-bold'>Fecha Desde:</label>
          <input
            type='date'
            value={fechaDesde}
            onChange={(e) => onFechaDesdeChange(e.target.value)}
            className='w-full p-2.5 text-base rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed'
            disabled={isLoading}
          />
        </div>

        <div>
          <label className='block mb-1 font-bold'>Fecha Hasta:</label>
          <input
            type='date'
            value={fechaHasta}
            onChange={(e) => onFechaHastaChange(e.target.value)}
            className='w-full p-2.5 text-base rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed'
            disabled={isLoading}
          />
        </div>
      </div>

      <div className='flex gap-2.5'>
        <button
          onClick={onSearch}
          disabled={isSearching || isLoading}
          className='px-5 py-2.5 text-base font-bold bg-blue-500 text-white border-none rounded cursor-pointer disabled:cursor-not-allowed disabled:opacity-60 hover:bg-blue-600 transition-colors'
        >
          {isSearching ? 'Buscando...' : 'Buscar'}
        </button>

        <button
          onClick={onClear}
          disabled={!hasActiveFilters}
          className='px-5 py-2.5 text-base bg-gray-100 text-gray-800 border border-gray-300 rounded cursor-pointer disabled:cursor-not-allowed disabled:opacity-60 hover:bg-gray-200 transition-colors'
        >
          Limpiar Filtros
        </button>
      </div>
    </div>
  )
}
