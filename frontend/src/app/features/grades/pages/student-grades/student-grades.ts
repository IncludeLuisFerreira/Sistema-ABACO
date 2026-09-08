import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { BreadcrumbComponent, BreadcrumbItem } from '../../../../shared/components/breadcrumb/breadcrumb';
import { Matricula } from '../../../../core/models/matricula.model';
import { Nota } from '../../../../core/models/nota.model';
import { MatriculaService } from '../../../../core/services/matricula.service';
import { NotaService } from '../../../../core/services/nota.service';

@Component({
  selector: 'app-student-grades',
  standalone: true,
  imports: [CommonModule, RouterLink, BreadcrumbComponent],
  templateUrl: './student-grades.html',
  styleUrls: ['./student-grades.scss'],
})
export class StudentGradesComponent implements OnInit {
  breadcrumbs: BreadcrumbItem[] = [
    { label: 'Admin', link: '/admin' },
    { label: 'Matrículas', link: '/admin/matriculas' },
    { label: 'Notas do Aluno' },
  ];
  notas: Nota[] = [];
  alunoNome = '';
  turmaNome = '';
  matriculaId = 0;

  loading = false;
  error: string | null = null;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly notaService: NotaService,
    private readonly matriculaService: MatriculaService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.matriculaId = Number(this.route.snapshot.paramMap.get('id'));
    if (this.matriculaId) {
      this.loadNotas();
    }
  }

  private loadNotas(): void {
    this.loading = true;
    this.error = null;

    this.notaService.listByMatricula(this.matriculaId).subscribe({
      next: (notas) => {
        this.notas = notas;
        if (notas.length > 0) {
          this.alunoNome = notas[0]?.matricula?.aluno?.nome ?? '';
          this.turmaNome = notas[0]?.matricula?.turma?.nomeCurso ?? '';
        } else {
          this.loadMatriculaInfo();
        }
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.error = 'Erro ao carregar as notas.';
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  private loadMatriculaInfo(): void {
    this.matriculaService.list().subscribe({
      next: (matriculas) => {
        const matricula = matriculas.find((m: Matricula) => m.idMatricula === this.matriculaId);
        if (matricula) {
          this.alunoNome = matricula.aluno?.nome ?? '';
          this.turmaNome = matricula.turma?.curso?.nomeCurso ?? '';
        }
        this.changeDetectorRef.detectChanges();
      },
      error: () => {},
    });
  }
}
