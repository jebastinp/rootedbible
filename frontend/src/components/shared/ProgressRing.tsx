interface Props {
  percentage: number
  size?: number
  strokeWidth?: number
  color?: string
  trackColor?: string
  className?: string
  children?: React.ReactNode
}

export default function ProgressRing({
  percentage,
  size = 96,
  strokeWidth = 9,
  color = '#79C141',
  trackColor = '#0B5D3B1A',
  className,
  children,
}: Props) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (Math.min(Math.max(percentage, 0), 100) / 100) * circumference

  return (
    <div className={`relative inline-flex items-center justify-center ${className ?? ''}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} stroke={trackColor} strokeWidth={strokeWidth} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s cubic-bezier(0.16,1,0.3,1)' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">{children}</div>
    </div>
  )
}
