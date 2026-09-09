import { Component, type ErrorInfo, type ReactNode } from 'react'

export default class AppErrorBoundary extends Component<
  { children: ReactNode },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Rooted could not render', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <main className="min-h-screen flex items-center justify-center px-6">
          <div className="max-w-sm bg-surface rounded-3xl p-7 shadow-card" role="alert">
            <h1 className="text-xl font-semibold text-primary">Rooted could not load this page</h1>
            <p className="my-4 text-sm">Please reload the page to try again.</p>
            <button className="bg-primary text-white rounded-xl px-4 py-3" onClick={() => window.location.reload()}>
              Reload page
            </button>
          </div>
        </main>
      )
    }
    return this.props.children
  }
}
