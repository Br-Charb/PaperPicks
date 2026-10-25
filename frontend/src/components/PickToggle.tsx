import { PickChoice } from '../types'

interface PickToggleProps {
  value?: PickChoice
  onChange: (choice: PickChoice) => void
  label: string
}

function PickToggle({ value, onChange, label }: PickToggleProps) {
  return (
    <div className="pick-toggle" aria-label={label}>
      <button
        className={value === 'over' ? 'selected' : ''}
        type="button"
        aria-pressed={value === 'over'}
        onClick={() => onChange('over')}
      >
        Over
      </button>
      <button
        className={value === 'under' ? 'selected' : ''}
        type="button"
        aria-pressed={value === 'under'}
        onClick={() => onChange('under')}
      >
        Under
      </button>
    </div>
  )
}

export default PickToggle
