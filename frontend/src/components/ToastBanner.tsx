import { useEffect } from 'react'
import { ToastMessage } from '../types'

interface ToastBannerProps {
  toast: ToastMessage | null
  onDismiss: () => void
}

function ToastBanner({ toast, onDismiss }: ToastBannerProps) {
  useEffect(() => {
    if (!toast) {
      return
    }
    const timer = window.setTimeout(onDismiss, 4500)
    return () => window.clearTimeout(timer)
  }, [toast, onDismiss])

  if (!toast) {
    return null
  }

  return (
    <div
      className={`toast-banner toast-banner--${toast.type}`}
      role={toast.type === 'success' ? 'status' : 'alert'}
      aria-live="assertive"
    >
      <div className="toast-banner__body">
        <strong>{toast.title}</strong>
        <p>{toast.message}</p>
      </div>
      <button
        type="button"
        className="toast-banner__close"
        aria-label="Dismiss notification"
        onClick={onDismiss}
      >
        ×
      </button>
    </div>
  )
}

export default ToastBanner
