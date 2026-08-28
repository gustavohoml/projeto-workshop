import type { ReactNode } from 'react'
import { Header } from './Header'
import { Footer } from './Footer'
import './layout.css'

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="layout">
      <Header />
      <main className="layout__main">{children}</main>
      <Footer />
    </div>
  )
}
