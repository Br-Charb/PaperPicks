interface PickToggleProps {
  label: string
}

function PickToggle({ label }: PickToggleProps) {
  return (
    <div className="pick-toggle" aria-label={label}>
      <button type="button" aria-pressed="false">Over</button>
      <button type="button" aria-pressed="false">Under</button>
    </div>
  )
}

export default PickToggle
