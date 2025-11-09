import { Outlet } from 'react-router-dom'

export function HomeLayout() {
  return (
    <div className='min-h-dvh bg-white'>
      {/* Header con link a GitHub */}
      <header className='sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm'>
        <div className='mx-auto w-full max-w-6xl px-6 py-3 flex justify-between items-center'>
          <div className='text-lg font-bold text-gray-800'>Votaciones del Congreso del Perú</div>
          <a
            href='https://github.com/NahumFGz/parliament-voting-web'
            target='_blank'
            rel='noopener noreferrer'
            className='flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors group'
            aria-label='Ver repositorio en GitHub'
          >
            <img
              src='/images/github-mark-white.svg'
              alt='GitHub'
              className='w-6 h-6 invert opacity-70 group-hover:opacity-100 transition-opacity'
            />
            <span className='text-sm font-medium text-gray-700 group-hover:text-gray-900 hidden sm:inline'>
              Repositorio
            </span>
          </a>
        </div>
      </header>

      <main className='mx-auto w-full max-w-6xl px-6'>
        <Outlet />
      </main>
    </div>
  )
}
