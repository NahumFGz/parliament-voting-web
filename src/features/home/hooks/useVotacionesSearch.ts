import { useState, useCallback, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useSearchWorker, type VotacionItem } from '../../../workers/useSearchWorker'

export function useVotacionesSearch() {
  const { search, isLoading, dataCount, error } = useSearchWorker()
  const [searchParams, setSearchParams] = useSearchParams()

  // Leer valores iniciales desde los query params
  const initialAsunto = searchParams.get('asunto') || ''
  const initialFechaDesde = searchParams.get('fechaDesde') || ''
  const initialFechaHasta = searchParams.get('fechaHasta') || ''

  // Estados de filtros
  const [asunto, setAsunto] = useState(initialAsunto)
  const [fechaDesde, setFechaDesde] = useState(initialFechaDesde)
  const [fechaHasta, setFechaHasta] = useState(initialFechaHasta)

  // Estados de resultados
  const [results, setResults] = useState<VotacionItem[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [displayLimit, setDisplayLimit] = useState(50)
  const [latestDate, setLatestDate] = useState<string>('')
  const [isInitialized, setIsInitialized] = useState(false)

  // Sincronizar query params con los filtros
  useEffect(() => {
    const params = new URLSearchParams()

    if (asunto) params.set('asunto', asunto)
    if (fechaDesde) params.set('fechaDesde', fechaDesde)
    if (fechaHasta) params.set('fechaHasta', fechaHasta)

    setSearchParams(params, { replace: true })
  }, [asunto, fechaDesde, fechaHasta, setSearchParams])

  // Cargar resultados iniciales cuando termine de cargar
  useEffect(() => {
    if (!isLoading && !hasSearched && !isInitialized) {
      const loadInitialResults = async () => {
        setIsSearching(true)
        setHasSearched(true)
        setIsInitialized(true)
        try {
          // Si hay filtros en la URL, buscar con esos filtros
          const hasUrlFilters = initialAsunto || initialFechaDesde || initialFechaHasta
          const searchResults = await search(
            hasUrlFilters
              ? {
                  asunto: initialAsunto,
                  fechaDesde: initialFechaDesde || undefined,
                  fechaHasta: initialFechaHasta || undefined
                }
              : {}
          )
          setResults(searchResults)
          if (searchResults.length > 0 && searchResults[0].fecha_hora) {
            setLatestDate(searchResults[0].fecha_hora)
          }
        } catch (err) {
          console.error('Error al cargar resultados iniciales:', err)
        } finally {
          setIsSearching(false)
        }
      }
      loadInitialResults()
    }
  }, [
    isLoading,
    hasSearched,
    search,
    isInitialized,
    initialAsunto,
    initialFechaDesde,
    initialFechaHasta
  ])

  // Realizar búsqueda con filtros
  const handleSearch = useCallback(async () => {
    setIsSearching(true)
    setHasSearched(true)

    try {
      const searchResults = await search({
        asunto: asunto,
        fechaDesde: fechaDesde || undefined,
        fechaHasta: fechaHasta || undefined
      })
      setResults(searchResults)
      setDisplayLimit(50)
    } catch (err) {
      console.error('Error en la búsqueda:', err)
    } finally {
      setIsSearching(false)
    }
  }, [search, asunto, fechaDesde, fechaHasta])

  // Limpiar todos los filtros
  const clearFilters = useCallback(() => {
    setAsunto('')
    setFechaDesde('')
    setFechaHasta('')
    setResults([])
    setHasSearched(false)
    setDisplayLimit(50)
    setSearchParams({}, { replace: true })
  }, [setSearchParams])

  // Cargar más resultados
  const loadMore = useCallback(() => {
    setDisplayLimit((prev) => prev + 50)
  }, [])

  return {
    // Estados de datos
    isLoading,
    dataCount,
    error,
    results,
    isSearching,
    hasSearched,
    displayLimit,
    latestDate,

    // Estados de filtros
    filters: {
      asunto,
      fechaDesde,
      fechaHasta
    },

    // Setters de filtros
    setAsunto,
    setFechaDesde,
    setFechaHasta,

    // Acciones
    handleSearch,
    clearFilters,
    loadMore
  }
}
