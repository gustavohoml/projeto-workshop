import { Link } from 'react-router-dom'

/** Placeholder honesto: diz em que etapa a tela entra, em vez de fingir
 *  uma interface que ainda nao existe. */
export function EmBreve({ titulo, etapa }: { titulo: string; etapa: number }) {
  return (
    <div className="shell embreve">
      <p className="eyebrow">{etapa > 0 ? `Etapa ${etapa}` : 'Rota desconhecida'}</p>
      <h1 className="embreve__t">{titulo}</h1>
      <p className="embreve__p">
        {etapa > 0
          ? 'Esta tela entra na etapa indicada, depois da validação da anterior. O desenvolvimento é incremental: uma etapa validada vale mais que cinco pela metade.'
          : 'Não há nada neste endereço.'}
      </p>
      <Link to="/" className="btn btn--ghost">Voltar ao início</Link>
    </div>
  )
}
