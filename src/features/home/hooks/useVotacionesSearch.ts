import { useState, useCallback, useEffect } from 'react'
import { useSearchWorker, type VotacionItem } from '../../../workers/useSearchWorker'

export function useVotacionesSearch() {
  const { search, isLoading, dataCount, error } = useSearchWorker()
  
  // Estados de filtros
  const [asunto, setAsunto] = useState('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  
  // Estados de resultados
  const [results, setResults] = useState<VotacionItem[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [displayLimit, setDisplayLimit] = useState(50)
  const [latestDate, setLatestDate] = useState<string>('')

  // Cargar resultados iniciales cuando termine de cargar
  useEffect(() => {
    if (!isLoading && !hasSearched) {
      const loadInitialResults = async () => {
        setIsSearching(true)
        setHasSearched(true)
        try {
          const searchResults = await search({})
          setResults(searchResults)
          if (searchResults.length > 0) {
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
  }, [isLoading, hasSearched, search])

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
  }, [])

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

