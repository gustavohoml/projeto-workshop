/** As quatro dimensoes da mesma decisao. Nao sao modulos independentes:
 *  Academico e o motor (Case 3); as outras tres sao consequencias da grade. */
export type DimensionId = 'academico' | 'carreira' | 'mobilidade' | 'campus'

export interface Dimension {
  id: DimensionId
  icon: string
  label: string
  case: string
  question: string
  detail: string
  route: string
}

export const DIMENSIONS: Dimension[] = [
  {
    id: 'academico', icon: '🎓', label: 'Acadêmico', case: 'Case 3',
    question: 'Quais grades são válidas?',
    detail: 'O motor de restrições: turmas indivisíveis, nenhum choque, preferências do aluno.',
    route: '/grade',
  },
  {
    id: 'carreira', icon: '💼', label: 'Carreira', case: 'Case 1',
    question: 'Que vagas cabem nesta grade?',
    detail: 'Curso, período e turno livre cruzados com os anúncios abertos na data de referência.',
    route: '/oportunidades',
  },
  {
    id: 'mobilidade', icon: '🚲', label: 'Mobilidade', case: 'Case 2',
    question: 'Como eu chego nesse horário?',
    detail: 'A primeira aula define a chegada; a chegada define a pressão na bike e no estacionamento.',
    route: '/mobilidade',
  },
  {
    id: 'campus', icon: '🍴', label: 'Campus', case: 'Case 4',
    question: 'O que faço nos intervalos?',
    detail: 'As janelas da grade cruzadas com orçamento, restrição alimentar e tempo disponível.',
    route: '/campus',
  },
]
