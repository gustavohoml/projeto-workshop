import { Link, useNavigate } from 'react-router-dom'
import { Wordmark } from './Wordmark'

export function Header() {
  const nav = useNavigate()
  return (
    <header className="hdr">
      <div className="shell hdr__in">
        <Link to="/" className="hdr__brand" aria-label="PUC Routine, ir para o início">
          <Wordmark />
        </Link>
        <button
          className="btn btn--ghost hdr__demo"
          onClick={() => nav('/?demo=true')}
          title="Percorre a história da Ana usando os mesmos motores do modo normal"
        >
          <span aria-hidden="true">▶</span> Executar Demo
        </button>
      </div>
    </header>
  )
}
