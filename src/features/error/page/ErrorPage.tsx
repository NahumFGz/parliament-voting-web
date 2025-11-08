import { Link } from 'react-router-dom'
import { ThemeSwitchButton } from '../../../components/ui/ThemeSwitchButton'

export function ErrorPage() {
  return (
    <section className='text-center'>
      <p className='text-base font-semibold text-indigo-600 dark:text-indigo-400'>404</p>

      <h1 className='mt-4 text-5xl font-semibold tracking-tight text-balance text-gray-900 dark:text-white sm:text-7xl'>
        Página no encontrada
      </h1>

      <p className='mt-6 text-lg font-medium text-pretty text-gray-500 dark:text-gray-400 sm:text-xl leading-8'>
        Lo sentimos, no pudimos encontrar la página que estás buscando.
      </p>

      <div className='mt-10 flex flex-col items-center gap-4'>
        <Link
          to='/'
          className='text-sm font-semibold text-gray-900 dark:text-white hover:underline'
        >
          Volver al inicio <span aria-hidden='true'>→</span>
        </Link>

        <ThemeSwitchButton />
      </div>
    </section>
  )
}
