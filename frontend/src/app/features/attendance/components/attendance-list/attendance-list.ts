import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface AttendanceStudentRow {
  idMatricula: number;
  nomeAluno: string;
  presente: boolean;
}

@Component({
  selector: 'app-attendance-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './attendance-list.html',
  styleUrls: ['./attendance-list.scss'],
})
export class AttendanceListComponent {
  @Input() students: AttendanceStudentRow[] = [];
  @Input() loading = false;
  @Input() dataAula = '';
  @Input() turmaNome = '';
  @Input() saving = false;

  @Output() readonly togglePresenca = new EventEmitter<number>();
  @Output() readonly dataAulaChange = new EventEmitter<string>();

  onDataAulaChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.dataAulaChange.emit(target.value);
  }

  onToggle(idMatricula: number): void {
    if (!this.saving) {
      this.togglePresenca.emit(idMatricula);
    }
  }
}
