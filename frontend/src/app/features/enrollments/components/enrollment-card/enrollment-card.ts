import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Matricula } from '../../../../core/models/matricula.model';

@Component({
  selector: 'app-enrollment-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './enrollment-card.html',
  styleUrls: ['./enrollment-card.scss'],
})
export class EnrollmentCardComponent {
  @Input() matricula!: Matricula;
  @Input() deleting = false;

  @Output() edit = new EventEmitter<Matricula>();
  @Output() remove = new EventEmitter<Matricula>();
  @Output() viewGrades = new EventEmitter<number>();
  @Output() viewTranscript = new EventEmitter<number>();

  get statusLabel(): string {
    const map: Record<number, string> = { 0: 'Ativa', 1: 'Concluída', 2: 'Cancelada' };
    return map[this.matricula.status ?? 0] ?? '—';
  }

  get statusClass(): string {
    const map: Record<number, string> = { 0: 'ativa', 1: 'concluida', 2: 'cancelada' };
    return map[this.matricula.status ?? 0] ?? '';
  }
}
