import { ChangeDetectorRef, Component, DestroyRef, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { timer } from 'rxjs';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
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
  private readonly destroyRef = inject(DestroyRef);
  totalTurmas = 0;
  totalAlunos = 0;
  loading = true;
  error: string | null = null;

  constructor(
    private readonly turmaService: TurmaService,
    private readonly matriculaService: MatriculaService,
    private readonly router: Router,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.turmaService.listMine().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (turmas: Turma[]) => {
        this.totalTurmas = turmas.length;

        if (turmas.length === 0) {
          this.loading = false;
          this.changeDetectorRef.markForCheck();
          timer(3000).pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => {
            void this.router.navigate(['/academico/turmas'], { replaceUrl: true });
          });
          return;
        }

        this.matriculaService.listMine().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
          next: (matriculas: Matricula[]) => {
            const alunosUnicos = new Set(matriculas.map((m) => m.idAluno));
            this.totalAlunos = alunosUnicos.size;
            this.loading = false;
            this.changeDetectorRef.markForCheck();
          },
          error: () => {
            this.error = 'Erro ao carregar alunos. Tente novamente mais tarde.';
            this.loading = false;
            this.changeDetectorRef.markForCheck();
          },
        });
      },
      error: () => {
        this.error = 'Erro ao carregar turmas. Tente novamente mais tarde.';
        this.loading = false;
        this.changeDetectorRef.markForCheck();
      },
    });
  }
}
