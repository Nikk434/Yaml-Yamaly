import './globals.css'

export const metadata = {
  title: 'YOLO YAML Generator',
  description: 'Collaborative class name management',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}