/** Procedencia de todo numero exibido. Nenhum valor vai para a tela sem uma
 *  destas marcacoes — e a regra central do produto. */
export type Procedencia =
  | 'observado'    // esta literalmente no arquivo entregue
  | 'calculado'    // derivado dos arquivos por um motor deste projeto
  | 'estimativa'   // modelo ou projecao, com erro conhecido
  | 'regra'        // decisao de produto (limiar, peso, filtro)
  | 'suposicao'    // hipotese assumida porque o dado nao existe

export const PROCEDENCIA_LABEL: Record<Procedencia, string> = {
  observado: 'Dado observado',
  calculado: 'Resultado calculado',
  estimativa: 'Estimativa',
  regra: 'Regra de negócio',
  suposicao: 'Suposição declarada',
}
