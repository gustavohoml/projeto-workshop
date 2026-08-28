/** Construcao herdada do brasao da PUC-Rio: palavra forte em preto,
 *  qualificador menor abaixo, filete separando. */
export function Wordmark({ size = 'sm' }: { size?: 'sm' | 'lg' }) {
  return (
    <span className={`wm wm--${size}`}>
      <span className="wm__main">PUC</span>
      <span className="wm__sub">ROUTINE</span>
    </span>
  )
}
