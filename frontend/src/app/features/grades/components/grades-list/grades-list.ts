import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Avaliacao } from '../../../../core/models/turma.model';

export interface GradeStudentRow {
  idMatricula: number;
  nomeAluno: string;
  nota: number | null;
}

interface ProvaOption {
  value: number;
  label: string;
  peso: number;
}

@Component({
  selector: 'app-grades-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './grades-list.html',
  styleUrls: ['./grades-list.scss'],
})
export class GradesListComponent {
  @Input() students: GradeStudentRow[] = [];
  @Input() loading = false;
  @Input() turmaNome = '';
  @Input() prova = 1;
  @Input() saving = false;
  @Input() avaliacoes: Avaliacao[] | null = null;

  @Output() readonly notaChange = new EventEmitter<{ idMatricula: number; nota: number | null }>();
  @Output() readonly provaChange = new EventEmitter<number>();

  get provaOptions(): ProvaOption[] {
    if (this.avaliacoes?.length) {
      return this.avaliacoes.map((a, i) => ({
        value: i + 1,
        label: a.nome || `Avaliação ${i + 1}`,
        peso: a.peso || 0,
      }));
    }
    return [1, 2, 3, 4].map((n) => ({
      value: n,
      label: `${n}ª Prova`,
      peso: 10,
    }));
  }

  onProvaChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.provaChange.emit(Number(target.value));
  }

  onNotaInput(idMatricula: number, event: Event): void {
    const target = event.target as HTMLInputElement;
    const value = target.value.trim();
    const nota = value === '' ? null : Number(value);
    this.notaChange.emit({ idMatricula, nota });
  }
}
