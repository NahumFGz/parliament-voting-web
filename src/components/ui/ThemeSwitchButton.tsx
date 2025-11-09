import { Icon } from '@iconify/react'
import { useThemeStoreDispatch } from '../../store/themeStore'

export function ThemeSwitchButton() {
  const { toggleTheme, theme } = useThemeStoreDispatch()

  return (
    <button
      type='button'
      onClick={toggleTheme}
      aria-label={`Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`}
      className={`flex h-9 w-9 items-center justify-center rounded-full text-white shadow-xs transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 ${
        theme === 'dark'
          ? 'bg-indigo-500 hover:bg-indigo-400 focus-visible:outline-indigo-500'
          : 'bg-indigo-600 hover:bg-indigo-500 focus-visible:outline-indigo-600'
      }`}
    >
      <span className='relative flex h-5 w-5 items-center justify-center'>
        <Icon
          icon='solar:sun-linear'
          width={20}
          className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transition-opacity duration-300 ease-in-out ${
            theme === 'dark' ? 'opacity-100' : 'opacity-0'
          }`}
        />
        <Icon
          icon='solar:moon-linear'
          width={18}
          className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 transition-opacity duration-300 ease-in-out ${
            theme === 'dark' ? 'opacity-0' : 'opacity-100'
          }`}
        />
      </span>
    </button>
  )
}
