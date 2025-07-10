#!/usr/bin/env python3
"""
    P-Way Merge Sort - Ordenação Externa
    MATA 54 - Estrutura de Dados e Algoritmos II - UFBA
"""

import sys
import os
import tempfile
from typing import List, Tuple, Optional

class MinHeap:
    def __init__(self):
        self.heap = []
    
    def push(self, item):
        self.heap.append(item)
        self._shift_up(len(self.heap) - 1)
    
    def pop(self):
        if not self.heap:
            return None
        self._swap(0, len(self.heap) - 1)
        item = self.heap.pop()
        self._shift_down(0)
        return item
    
    def peek(self):
        return self.heap[0] if self.heap else None
    
    def __len__(self):
        return len(self.heap)
    
    def _shift_up(self, index):
        parent = (index - 1) // 2
        while index > 0 and self.heap[index] < self.heap[parent]:
            self._swap(index, parent)
            index = parent
            parent = (index - 1) // 2
    
    def _shift_down(self, index):
        left = 2 * index + 1
        right = 2 * index + 2
        smallest = index
        
        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right
        
        if smallest != index:
            self._swap(index, smallest)
            self._sift_down(smallest)
    
    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

class PWayMergeSort:
    def __init__(self, p: int):
        if p < 2:
            raise ValueError("p deve ser >= 2")
        self.p = p
        self.temp_files = []
        self.num_runs = 0
        self.num_passes = 0
        self.num_records = 0
    
    def replacement_selection(self, input_file: str) -> List[str]:
        runs = []
        next_run_buffer = []
        last_output = None
        
        with open(input_file, 'r') as f:
            heap = MinHeap()

            for _ in range(self.p):
                line = f.readline().strip()
                if not line:
                    break
                value = int(line)
                heap.push(value)
                self.num_records += 1
            
            if not heap:
                return runs
            
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
            self.temp_files.append(temp_file.name)
            current_run_file = temp_file

            while heap or next_run_buffer:
                if heap:
                    min_val = heap.pop()
                    
                    if last_output is None or min_val >= last_output:
                        current_run_file.write(f"{min_val}\n")
                        last_output = min_val
                    else:
                        next_run_buffer.append(min_val)
                    
                    line = f.readline().strip()
                    if line:
                        value = int(line)
                        self.num_records += 1
                        
                        if last_output is None or value >= last_output:
                            heap.push(value)
                        else:
                            next_run_buffer.append(value)
                else:
                    current_run_file.close()
                    runs.append(current_run_file.name)

                    for item in next_run_buffer:
                        heap.push(item)
                    next_run_buffer = []
                    last_output = None

                    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                    self.temp_files.append(temp_file.name)
                    current_run_file = temp_file

            current_run_file.close()
            runs.append(current_run_file.name)
        
        self.num_runs = len(runs)
        return runs
    
    def merge_runs(self, input_runs: List[str]) -> List[str]:
        if len(input_runs) <= 1:
            return input_runs
        
        output_runs = []
        
        for i in range(0, len(input_runs), self.p):
            group = input_runs[i:i+self.p]
            merged_file = self._merge_group(group)
            output_runs.append(merged_file)
        
        return output_runs
    
    def _merge_group(self, run_files: List[str]) -> str:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_files.append(temp_file.name)
        output_file = temp_file

        file_handles = []
        heap = MinHeap()
        
        for i, filename in enumerate(run_files):
            f = open(filename, 'r')
            file_handles.append(f)

            line = f.readline().strip()
            if line:
                value = int(line)
                heap.push((value, i))

        while heap:
            min_val, file_idx = heap.pop()
            output_file.write(f"{min_val}\n")

            line = file_handles[file_idx].readline().strip()
            if line:
                value = int(line)
                heap.push((value, file_idx))

        for f in file_handles:
            f.close()
        output_file.close()
        
        return output_file.name
    
    def sort_file(self, input_file: str, output_file: str) -> None:
        formatted_input = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_files.append(formatted_input.name)
        
        with open(input_file, 'r') as f_in:
            for line in f_in:
                numbers = line.strip().split()
                for num in numbers:
                    if num:  
                        formatted_input.write(f"{num}\n")
        formatted_input.close()

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
        return (self.num_records, self.p, self.num_runs, self.num_passes)

def main():
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

        sorter = PWayMergeSort(p)
        sorter.sort_file(input_file, output_file)

        num_records, ways, num_runs, num_passes = sorter.get_stats()
        print("#Regs Ways #Runs #Parses")
        print(f"{num_records} {ways} {num_runs} {num_passes}")

        sorter.cleanup()
        
    except ValueError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()