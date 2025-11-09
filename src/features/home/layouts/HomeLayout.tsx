import { Outlet } from 'react-router-dom'

export function HomeLayout() {
  return (
    <div className='min-h-dvh bg-white'>
      <main className='mx-auto w-full max-w-6xl px-6'>
        <Outlet />
      </main>
    </div>
  )
}
