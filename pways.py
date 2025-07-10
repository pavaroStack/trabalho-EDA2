#!/usr/bin/env python3
"""
P-Way Merge Sort - Ordenação Externa
MATA 54 - Estrutura de Dados e Algoritmos II - UFBA
"""

import sys
import os
import heapq
import tempfile
from typing import List, Tuple, Optional

class PWayMergeSort:
    def __init__(self, p: int):
        """
        Inicializa o algoritmo de ordenação externa p-way merge sort.
        
        Args:
            p: Número de caminhos (ways) - limita memória a p registros
        """
        if p < 2:
            raise ValueError("p deve ser >= 2")
        self.p = p
        self.temp_files = []
        self.num_runs = 0
        self.num_passes = 0
        self.num_records = 0
        
    def replacement_selection(self, input_file: str) -> List[str]:
        runs = []
        heap = []
        next_run_buffer = []
        last_output = None
        self.num_records = 0

        with open(input_file, 'r') as f:
            # Carrega os primeiros p registros
            for _ in range(self.p):
                line = f.readline().strip()
                if not line: 
                    break
                value = int(line)
                heapq.heappush(heap, value)
                self.num_records += 1

            # Cria primeiro arquivo temporário
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
            self.temp_files.append(temp_file.name)
            current_run_file = temp_file

            while heap:
                min_val = heapq.heappop(heap)
                
                # Escreve na run atual
                if last_output is None or min_val >= last_output:
                    current_run_file.write(f"{min_val}\n")
                    last_output = min_val
                else:
                    # Se não pode escrever na run atual, coloca no buffer
                    next_run_buffer.append(min_val)
                
                # Lê próximo registro
                line = f.readline().strip()
                if line:
                    value = int(line)
                    self.num_records += 1
                    
                    if last_output is None or value >= last_output:
                        heapq.heappush(heap, value)
                    else:
                        next_run_buffer.append(value)
                
                # Se heap esvaziou mas temos registros no buffer
                if not heap and next_run_buffer:
                    # Finaliza run atual
                    current_run_file.close()
                    runs.append(current_run_file.name)
                    
                    # Reinicia para nova run
                    heap = next_run_buffer
                    heapq.heapify(heap)
                    next_run_buffer = []
                    last_output = None
                    
                    # Cria novo arquivo
                    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                    self.temp_files.append(temp_file.name)
                    current_run_file = temp_file

            # Finaliza última run
            current_run_file.close()
            runs.append(current_run_file.name)
        
        self.num_runs = len(runs)
        return runs
    
    def merge_runs(self, input_runs: List[str]) -> List[str]:
        """
        Intercala sequências ordenadas usando heap mínima.
        
        Args:
            input_runs: Lista de arquivos com sequências ordenadas
            
        Returns:
            Lista com arquivos resultantes da intercalação
        """
        if len(input_runs) <= 1:
            return input_runs
        
        output_runs = []
        
        # Processa grupos de p sequências por vez
        for i in range(0, len(input_runs), self.p):
            group = input_runs[i:i+self.p]
            merged_file = self._merge_group(group)
            output_runs.append(merged_file)
        
        return output_runs
    
    def _merge_group(self, run_files: List[str]) -> str:
        """
        Intercala um grupo de sequências ordenadas.
        
        Args:
            run_files: Lista de arquivos a serem intercalados
            
        Returns:
            Nome do arquivo resultante da intercalação
        """
        # Cria arquivo temporário para saída
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_files.append(temp_file.name)
        output_file = temp_file
        
        # Abre todos os arquivos de entrada
        file_handles = []
        heap = []
        
        for i, filename in enumerate(run_files):
            f = open(filename, 'r')
            file_handles.append(f)
            
            # Lê primeiro registro de cada arquivo
            line = f.readline().strip()
            if line:
                value = int(line)
                heapq.heappush(heap, (value, i))
        
        # Intercala usando heap mínima
        while heap:
            min_val, file_idx = heapq.heappop(heap)
            output_file.write(f"{min_val}\n")
            
            # Lê próximo registro do mesmo arquivo
            line = file_handles[file_idx].readline().strip()
            if line:
                value = int(line)
                heapq.heappush(heap, (value, file_idx))
        
        # Fecha arquivos
        for f in file_handles:
            f.close()
        output_file.close()
        
        return output_file.name
    
    def sort_file(self, input_file: str, output_file: str) -> None:
    # Cria arquivo temporário formatado (um número por linha)
        formatted_input = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_files.append(formatted_input.name)
        
        with open(input_file, 'r') as f_in:
            for line in f_in:
                # Processa cada número na linha
                numbers = line.strip().split()
                for num in numbers:
                    if num:  # Verifica se não é string vazia
                        formatted_input.write(f"{num}\n")
        formatted_input.close()

        # Usa o arquivo formatado como entrada
        runs = self.replacement_selection(formatted_input.name)
        
        if not runs:
            with open(output_file, 'w') as f:
                pass
            return

        self.num_passes = 0
        while len(runs) > 1:
            runs = self.merge_runs(runs)
            self.num_passes += 1
        
        if runs:
            with open(runs[0], 'r') as src, open(output_file, 'w') as dst:
                dst.write(src.read())
    
    def cleanup(self) -> None:
        """Remove arquivos temporários."""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
    
    def get_stats(self) -> Tuple[int, int, int, int]:
        """
        Retorna estatísticas da ordenação.
        
        Returns:
            Tupla (num_records, p, num_runs, num_passes)
        """
        return (self.num_records, self.p, self.num_runs, self.num_passes)

def main():
    """Função principal do programa."""
    if len(sys.argv) != 4:
        print("Uso: python pways.py <p> <arquivo_entrada> <arquivo_saida>")
        sys.exit(1)
    
    try:
        p = int(sys.argv[1])
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        if p < 2:
            print("Erro: p deve ser >= 2")
            sys.exit(1)
        
        if not os.path.exists(input_file):
            print(f"Erro: Arquivo de entrada '{input_file}' não encontrado")
            sys.exit(1)
        
        # Executa ordenação
        sorter = PWayMergeSort(p)
        sorter.sort_file(input_file, output_file)
        
        # Exibe estatísticas
        num_records, ways, num_runs, num_passes = sorter.get_stats()
        print("#Regs Ways #Runs #Parses")
        print(f"{num_records} {ways} {num_runs} {num_passes}")
        
        # Limpa arquivos temporários
        sorter.cleanup()
        
    except ValueError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()