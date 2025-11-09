import { Outlet } from 'react-router-dom'
import { useState } from 'react'

export function HomeLayout() {
  const [showCopiedMessage, setShowCopiedMessage] = useState(false)

  const handleShare = async () => {
    try {
      const currentUrl = window.location.href
      await navigator.clipboard.writeText(currentUrl)
      setShowCopiedMessage(true)
      setTimeout(() => setShowCopiedMessage(false), 2000)
    } catch (err) {
      console.error('Error al copiar URL:', err)
    }
  }

  return (
    <div className='min-h-dvh bg-white'>
      {/* Header con botón de compartir */}
      <header className='sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm'>
        <div className='mx-auto w-full max-w-6xl px-6 py-3 flex justify-between items-center'>
          <div className='text-lg font-bold text-gray-800'>Votaciones del Congreso del Perú</div>
          <div className='relative'>
            <button
              onClick={handleShare}
              className='flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors group'
              aria-label='Compartir URL actual'
              title='Compartir URL'
            >
              <img
                src='/images/share.svg'
                alt='Compartir'
                className='w-6 h-6 opacity-70 group-hover:opacity-100 transition-opacity'
              />
              <span className='text-sm font-medium text-gray-700 group-hover:text-gray-900 hidden sm:inline'>
                Compartir
              </span>
            </button>
            {showCopiedMessage && (
              <div className='absolute top-full right-0 mt-2 px-3 py-2 bg-green-600 text-white text-sm rounded-lg shadow-lg whitespace-nowrap'>
                ✓ URL copiada
              </div>
            )}
          </div>
        </div>
      </header>

      <main className='mx-auto w-full max-w-6xl px-6'>
        <Outlet />
      </main>
    </div>
  )
}
