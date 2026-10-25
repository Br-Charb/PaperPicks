interface DateSeparatorProps {
  date: string
}

function DateSeparator({ date }: DateSeparatorProps) {
  const [month, day, year] = date.split('/')

  return (
    <div className="date-separator">
      <span />
      <time dateTime={`${year}-${month}-${day}`}>{date}</time>
      <span />
    </div>
  )
}

export default DateSeparator
