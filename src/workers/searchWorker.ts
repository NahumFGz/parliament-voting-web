interface VotacionItem {
  id: string
  tipo: string | null
  fecha_hora: string | null
  asunto: string | null
  pagina: string
  url: string
}

interface SearchParams {
  asunto?: string
  fechaDesde?: string
  fechaHasta?: string
}

let votacionesData: VotacionItem[] = []
let dataLoaded = false

// Normalizar texto para búsqueda: sin tildes, minúsculas, sin puntuación
function normalizeText(text: string | null): string {
  if (!text) return ''
  return text
    .toLowerCase()
    .normalize('NFD') // Descompone caracteres con acentos
    .replace(/[\u0300-\u036f]/g, '') // Elimina los diacríticos (tildes)
    .replace(/[^\w\s]/g, '') // Elimina puntuación
    .replace(/\s+/g, ' ') // Normaliza espacios múltiples a uno solo
    .trim()
}

// Cargar datos al iniciar el worker
async function loadData() {
  if (dataLoaded) return

  try {
    const response = await fetch('/db/encabezados_unificados.json')
    if (!response.ok) {
      throw new Error(`Error al cargar datos: ${response.status}`)
    }
    votacionesData = await response.json()
    dataLoaded = true
    self.postMessage({ type: 'data_loaded', count: votacionesData.length })
  } catch (error) {
    self.postMessage({
      type: 'error',
      message: error instanceof Error ? error.message : 'Error desconocido'
    })
  }
}

// Función de búsqueda
function search(params: SearchParams): VotacionItem[] {
  if (!dataLoaded) {
    return []
  }

  let results = [...votacionesData]

  // Filtrar por asunto (búsqueda flexible sin tildes ni puntuación)
  if (params.asunto && params.asunto.trim() !== '') {
    const normalizedSearch = normalizeText(params.asunto)
    results = results.filter((item) => {
      const normalizedAsunto = normalizeText(item.asunto)
      return normalizedAsunto.includes(normalizedSearch)
    })
  }

  // Filtrar por fecha desde
  if (params.fechaDesde) {
    const fechaDesde = new Date(params.fechaDesde)
    results = results.filter((item) => {
      if (!item.fecha_hora) return false
      const itemFecha = new Date(item.fecha_hora)
      return !isNaN(itemFecha.getTime()) && itemFecha >= fechaDesde
    })
  }

  // Filtrar por fecha hasta
  if (params.fechaHasta) {
    const fechaHasta = new Date(params.fechaHasta)
    // Agregar 23:59:59 al día seleccionado
    fechaHasta.setHours(23, 59, 59, 999)
    results = results.filter((item) => {
      if (!item.fecha_hora) return false
      const itemFecha = new Date(item.fecha_hora)
      return !isNaN(itemFecha.getTime()) && itemFecha <= fechaHasta
    })
  }

  // Ordenar por fecha (más reciente primero)
  // Los items sin fecha van al final
  results.sort((a, b) => {
    if (!a.fecha_hora && !b.fecha_hora) return 0
    if (!a.fecha_hora) return 1
    if (!b.fecha_hora) return -1
    
    const fechaA = new Date(a.fecha_hora)
    const fechaB = new Date(b.fecha_hora)
    
    // Si alguna fecha es inválida, ponerla al final
    if (isNaN(fechaA.getTime()) && isNaN(fechaB.getTime())) return 0
    if (isNaN(fechaA.getTime())) return 1
    if (isNaN(fechaB.getTime())) return -1
    
    return fechaB.getTime() - fechaA.getTime()
  })

  return results
}

// Escuchar mensajes del hilo principal
self.addEventListener('message', async (event) => {
  const { type, params } = event.data

  switch (type) {
    case 'load':
      await loadData()
      break

    case 'search': {
      if (!dataLoaded) {
        await loadData()
      }
      const results = search(params)
      self.postMessage({
        type: 'search_results',
        results,
        count: results.length
      })
      break
    }

    default:
      self.postMessage({
        type: 'error',
        message: `Tipo de mensaje desconocido: ${type}`
      })
  }
})

// Exportar para TypeScript (no se ejecuta en runtime)
export {}
