import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Agents4Energy - Generative AI for Energy Industry',
  description: 'Open-source agentic workflows for energy industry professionals - reservoir characterization, well workover assessment, field data analysis, supply chain optimization, and asset integrity management.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Plotly.js CDN for reliable loading of interactive charts */}
        <script
          src="https://cdn.plot.ly/plotly-latest.min.js"
          async
          defer
        />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}