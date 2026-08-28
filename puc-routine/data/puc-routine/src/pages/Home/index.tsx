import { Link } from 'react-router-dom'
import { Wordmark } from '@/components/layout/Wordmark'
import { DIMENSIONS } from '@/constants/dimensions'
import './home.css'

export function Home() {
  return (
    <>
      <section className="shell hero">
        <p className="eyebrow hero__eyebrow">Impact Lab · SIEng 2026 · PUC-Rio</p>
        <Wordmark size="lg" />
        <h1 className="hero__tag">A rotina acadêmica como sistema de decisão.</h1>
        <p className="hero__lede">
          A grade define quando você pode trabalhar, a que horas precisa chegar à PUC e
          quais intervalos tem durante o dia. O PUC Routine não procura uma grade válida —
          ele compara configurações de semestre e torna explícito o que você está trocando.
        </p>
        <div className="hero__cta">
          <Link to="/perfil" className="btn">Planejar meu semestre</Link>
          <Link to="/?demo=true" className="btn btn--ghost"><span aria-hidden="true">▶</span> Executar Demo</Link>
        </div>
      </section>

      <section className="shell dims">
        <div className="dims__head">
          <h2 className="dims__t">Quatro decisões ligadas. Um único sistema.</h2>
          <p className="dims__p">
            Hoje elas vivem em quatro lugares que não conversam: o SGU, o Vagas Online, a
            cancela do estacionamento e o quadro de cada restaurante. Aqui são dimensões da
            mesma escolha — e todas as três últimas são consequência da primeira.
          </p>
        </div>
        <div className="dims__grid">
          {DIMENSIONS.map((d, i) => (
            <article key={d.id} className={`dim ${i === 0 ? 'dim--core' : ''}`}>
              <div className="dim__top">
                <span className="dim__icon" aria-hidden="true">{d.icon}</span>
                <span className="dim__case">{d.case}</span>
              </div>
              <h3 className="dim__label">{d.label}</h3>
              <p className="dim__q">{d.question}</p>
              <p className="dim__d">{d.detail}</p>
              {i === 0 && <span className="dim__flag">motor</span>}
            </article>
          ))}
        </div>
      </section>

      <section className="shell thesis">
        <div className="thesis__rule" />
        <p className="thesis__t">
          O solver garante que a grade é <strong>válida</strong>.
          A IA explica por que uma grade válida é <strong>melhor para você</strong> que outra.
        </p>
        <p className="thesis__p">
          Cada número exibido no produto carrega sua procedência: dado observado, resultado
          calculado, estimativa, regra de negócio ou suposição declarada. Onde o dado não
          existe, o sistema diz que não existe.
        </p>
      </section>
    </>
  )
}
