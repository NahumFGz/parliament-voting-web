import { Outlet } from 'react-router-dom'

export function ErrorLayout() {
  return (
    <div className='min-h-dvh grid place-items-center px-6 py-24 sm:py-32 lg:px-8 bg-white'>
      <main role='main' className='w-full'>
        <Outlet />
      </main>
    </div>
  )
}
