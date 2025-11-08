import { Icon } from '@iconify/react'
import { useThemeStoreDispatch } from '../../store/themeStore'

export function ThemeSwitchButton() {
  const { toggleTheme, theme } = useThemeStoreDispatch()

  return (
    <div className='relative inline-flex items-center group'>
      <button
        type='button'
        onClick={toggleTheme}
        className='inline-flex h-10 w-10 items-center justify-center rounded-full border border-transparent bg-transparent text-foreground transition hover:bg-muted focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background focus:ring-primary'
        aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      >
        <span className='relative w-6 h-6'>
          <Icon
            icon='solar:sun-linear'
            width={24}
            className={`absolute inset-0 transition-opacity duration-300 ease-in-out ${
              theme === 'dark' ? 'opacity-100' : 'opacity-0'
            }`}
          />
          <Icon
            icon='solar:moon-linear'
            width={22}
            className={`absolute inset-0 transition-opacity duration-300 ease-in-out ${
              theme === 'dark' ? 'opacity-0' : 'opacity-100'
            }`}
          />
        </span>
      </button>
      <span className='pointer-events-none absolute left-1/2 top-full z-10 mt-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-foreground px-2 py-1 text-xs font-medium text-background opacity-0 shadow-lg transition-opacity duration-150 group-hover:opacity-100'>
        {`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      </span>
    </div>
  )
}
