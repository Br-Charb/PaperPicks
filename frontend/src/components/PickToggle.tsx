import { PickChoice } from '../types'

interface PickToggleProps {
  value?: PickChoice
  onChange: (choice: PickChoice) => void
  label: string
  disabled?: boolean
}

function PickToggle({ value, onChange, label, disabled }: PickToggleProps) {
  return (
    <div className="pick-toggle" aria-label={label}>
      <button
        className={value === 'over' ? 'selected' : ''}
        type="button"
        aria-pressed={value === 'over'}
        disabled={disabled}
        onClick={() => onChange('over')}
      >
        Over
      </button>
      <button
        className={value === 'under' ? 'selected' : ''}
        type="button"
        aria-pressed={value === 'under'}
        disabled={disabled}
        onClick={() => onChange('under')}
      >
        Under
      </button>
    </div>
  )
}

export default PickToggle
