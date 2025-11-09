import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { HomeLayout } from '../features/home/layouts/HomeLayout'
import { HomePage } from '../features/home/pages/HomePage'
import { ErrorLayout } from '../features/error/layouts/ErrorLayout'
import { ErrorPage } from '../features/error/page/ErrorPage'

export function Navigation() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<HomeLayout />}>
          <Route path='/' element={<HomePage />} />
        </Route>

        {/* Rutas para error */}
        <Route element={<ErrorLayout />}>
          <Route path='*' element={<ErrorPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
