export function formatDate(dateString: string | null): string {
  if (!dateString) return 'Fecha no disponible'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'Fecha inválida'
  return date.toLocaleString('es-PE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
