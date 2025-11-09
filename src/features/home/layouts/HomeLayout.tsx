import { Outlet } from 'react-router-dom'

export function HomeLayout() {
  return (
    <div className='min-h-dvh bg-white'>
      <main className='mx-auto w-full max-w-6xl px-6 py-10 sm:py-16'>
        <Outlet />
      </main>
    </div>
  )
}
