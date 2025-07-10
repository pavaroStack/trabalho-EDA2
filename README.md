# Universidade Federal da Bahia (UFBA)

Instituto de Computação (IC)  
Departamento de Ciência da Computação (DCC)  
**MATA 54 - Estrutura de Dados e Algoritmos II – 2025.1 – Prof. George Lima**

## Especificação do Trabalho

### Objetivo

O trabalho tem como objetivo consolidar o conhecimento sobre as características do problema de ordenação externa. O estudante deverá entregar código-fonte livre de erros que possa ser compilado e executado conforme esta especificação. O programa deve ser capaz de ordenar um arquivo de entrada considerando restrições de tamanho de memória interna e número de arquivos manipulados simultaneamente.

### Método de Ordenação

- **Algoritmo**: Ordenação balanceada de p-caminhos (p-way merge sort)
- **Restrição de memória**: Memória principal não pode conter mais que `p` registros
- **Geração de sequências iniciais**: Usar **seleção por substituição**
- **Intercalação**: Baseada em heap mínima para até `p` sequências
- **Manipulação de arquivos**: Máximo de `2p` arquivos manipulados simultaneamente

### Interface de Entrada/Saída

**Execução**:

```bash
./pways <p> <arquivo_entrada> <arquivo_saída>
```
