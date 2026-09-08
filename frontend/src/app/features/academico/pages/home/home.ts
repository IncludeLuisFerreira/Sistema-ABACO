import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TurmaService } from '../../../../core/services/turma.service';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { Turma } from '../../../../core/models/turma.model';
import { Matricula } from '../../../../core/models/matricula.model';

@Component({
  selector: 'app-academico-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './home.html',
  styleUrls: ['./home.scss'],
})
export class AcademicoHome implements OnInit {
  totalTurmas = 0;
  totalAlunos = 0;
  loading = true;

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
  ) {}

  ngOnInit(): void {
    this.turmaService.listMine().subscribe({
      next: (turmas: Turma[]) => {
        this.totalTurmas = turmas.length;

        if (turmas.length === 0) {
          this.loading = false;
          return;
        }

        this.matriculaService.listMine().subscribe({
          next: (matriculas: Matricula[]) => {
            const alunosUnicos = new Set(matriculas.map((m) => m.idAluno));
            this.totalAlunos = alunosUnicos.size;
            this.loading = false;
          },
          error: () => { this.loading = false; },
        });
      },
      error: () => { this.loading = false; },
    });
  }
}
