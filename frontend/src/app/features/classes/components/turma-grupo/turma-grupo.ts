import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Turma } from '../../../../core/models/turma.model';
import { TurmaCardComponent } from '../turma-card/turma-card';

export interface TurmaGrupo {
  cursoNome: string;
  turmas: Turma[];
  expandido: boolean;
}

@Component({
  selector: 'app-turma-grupo',
  standalone: true,
  imports: [CommonModule, TurmaCardComponent],
  templateUrl: './turma-grupo.html',
  styleUrls: ['./turma-grupo.scss'],
})
export class TurmaGrupoComponent {
  @Input() grupo!: TurmaGrupo;
  @Input() deletingTurmaId: number | null = null;

  @Output() toggle = new EventEmitter<string>();
  @Output() edit = new EventEmitter<Turma>();
  @Output() remove = new EventEmitter<Turma>();
  @Output() duplicate = new EventEmitter<Turma>();
}
