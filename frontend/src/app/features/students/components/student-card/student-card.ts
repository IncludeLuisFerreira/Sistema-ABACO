import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Aluno } from '../../../../core/models/aluno.model';

@Component({
  selector: 'app-student-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './student-card.html',
  styleUrls: ['./student-card.scss'],
})
export class StudentCardComponent {
  @Input() aluno!: Aluno;
  @Input() deleting = false;

  @Output() edit = new EventEmitter<Aluno>();
  @Output() remove = new EventEmitter<Aluno>();

  get endereco(): string {
    const parts = [this.aluno.rua, this.aluno.numero ? String(this.aluno.numero) : '', this.aluno.bairro].filter(Boolean);
    return parts.length > 0 ? parts.join(', ') : '—';
  }
}
