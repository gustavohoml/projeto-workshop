import { Routes, Route } from 'react-router-dom'
import { Home } from '@/pages/Home'
import { EmBreve } from '@/components/layout/EmBreve'

/** As telas seguintes entram uma por etapa validada. Ate la, cada rota
 *  responde com o que sera construido — nunca com uma tela falsa. */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/perfil" element={<EmBreve titulo="Perfil" etapa={2} />} />
      <Route path="/disciplinas" element={<EmBreve titulo="Disciplinas" etapa={3} />} />
      <Route path="/grade" element={<EmBreve titulo="Grade" etapa={4} />} />
      <Route path="/oportunidades" element={<EmBreve titulo="Carreira" etapa={5} />} />
      <Route path="/mobilidade" element={<EmBreve titulo="Mobilidade" etapa={6} />} />
      <Route path="/campus" element={<EmBreve titulo="Vida no campus" etapa={7} />} />
      <Route path="/semestre" element={<EmBreve titulo="Meu semestre" etapa={9} />} />
      <Route path="/test-lab" element={<EmBreve titulo="Test Lab" etapa={10} />} />
      <Route path="*" element={<EmBreve titulo="Página não encontrada" etapa={0} />} />
    </Routes>
  )
}
