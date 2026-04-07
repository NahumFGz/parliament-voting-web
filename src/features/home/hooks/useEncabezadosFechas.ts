import { useState, useEffect } from 'react'

type EncabezadosFechasJson = {
  fecha_min: string
  fecha_max: string
}

/** fechas min/max según public/db/encabezados_fechas.json */
export function useEncabezadosFechas() {
  const [oldestDate, setOldestDate] = useState<string>('')
  const [latestDate, setLatestDate] = useState<string>('')

  useEffect(() => {
    let cancelled = false
    fetch('/db/encabezados_fechas.json')
      .then((r) => r.json() as Promise<EncabezadosFechasJson>)
      .then((data) => {
        if (cancelled) return
        if (data.fecha_min) setOldestDate(data.fecha_min)
        if (data.fecha_max) setLatestDate(data.fecha_max)
      })
      .catch(() => {
        /* banner sin fechas si falla la carga */
      })
    return () => {
      cancelled = true
    }
  }, [])

  return { oldestDate, latestDate }
}
