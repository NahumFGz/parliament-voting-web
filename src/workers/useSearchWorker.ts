import { useEffect, useRef, useState, useCallback } from 'react'

export interface VotacionItem {
  id: string
  tipo: string | null
  fecha_hora: string | null
  asunto: string | null
  pagina: string
  url: string
}

export interface SearchParams {
  asunto?: string
  fechaDesde?: string
  fechaHasta?: string
}

export function useSearchWorker() {
  const workerRef = useRef<Worker | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [dataCount, setDataCount] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Crear el worker
    workerRef.current = new Worker(new URL('./searchWorker.ts', import.meta.url), {
      type: 'module'
    })

    // Configurar el listener para mensajes del worker
    workerRef.current.onmessage = (event) => {
      const { type, count, message } = event.data

      if (type === 'data_loaded') {
        setIsLoading(false)
        setDataCount(count)
        setError(null)
      } else if (type === 'error') {
        setIsLoading(false)
        setError(message)
      }
    }

    // Cargar los datos inicialmente
    workerRef.current.postMessage({ type: 'load' })

    // Cleanup
    return () => {
      workerRef.current?.terminate()
    }
  }, [])

  const search = useCallback((params: SearchParams): Promise<VotacionItem[]> => {
    return new Promise((resolve, reject) => {
      if (!workerRef.current) {
        reject(new Error('Worker no está inicializado'))
        return
      }

      const handleMessage = (event: MessageEvent) => {
        const { type, results, message } = event.data

        if (type === 'search_results') {
          workerRef.current?.removeEventListener('message', handleMessage)
          resolve(results)
        } else if (type === 'error') {
          workerRef.current?.removeEventListener('message', handleMessage)
          reject(new Error(message))
        }
      }

      workerRef.current.addEventListener('message', handleMessage)
      workerRef.current.postMessage({ type: 'search', params })
    })
  }, [])

  return {
    search,
    isLoading,
    dataCount,
    error
  }
}
