const dateTimeFormat = new Intl.DateTimeFormat('pl-PL', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
})

export function formatDateTime(input) {
  if (!input) return '—'
  const date = typeof input === 'string' || typeof input === 'number' ? new Date(input) : input
  if (Number.isNaN(date.getTime())) return '—'
  return dateTimeFormat.format(date)
}

export function formatDuration(seconds) {
  if (seconds === undefined || seconds === null || Number.isNaN(Number(seconds))) return '—'
  const totalSeconds = Math.max(0, Math.floor(Number(seconds)))
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const secs = totalSeconds % 60
  return [hours, minutes, secs]
    .map((val) => val.toString().padStart(2, '0'))
    .join(':')
}
