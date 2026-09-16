import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

import { BreadcrumbComponent, BreadcrumbItem } from '../../../../shared/components/breadcrumb/breadcrumb';
import { Historico } from '../../../../core/models/historico.model';
import { HistoricoService } from '../../../../core/services/historico.service';

@Component({
  selector: 'app-transcript-view',
  standalone: true,
  imports: [CommonModule, BreadcrumbComponent],
  templateUrl: './transcript-view.html',
  styleUrls: ['./transcript-view.scss'],
})
export class TranscriptViewComponent implements OnInit {
  breadcrumbs: BreadcrumbItem[] = [
    { label: 'Admin', link: '/admin' },
    { label: 'Matrículas', link: '/admin/matriculas' },
    { label: 'Histórico Escolar' },
  ];
  historico: Historico | null = null;
  loading = false;
  error: string | null = null;
  gerandoPdf = false;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly historicoService: HistoricoService,
    private readonly changeDetectorRef: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    const matriculaId = this.route.snapshot.paramMap.get('id');
    if (!matriculaId) {
      this.error = 'ID da matricula nao informado.';
      return;
    }
    this.load(Number(matriculaId));
  }

  private load(matriculaId: number): void {
    this.loading = true;
    this.error = null;
    this.historicoService.getByMatricula(matriculaId).subscribe({
      next: (data) => {
        this.historico = data;
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      },
      error: () => {
        this.error = 'Erro ao carregar historico escolar.';
        this.loading = false;
        this.changeDetectorRef.detectChanges();
      },
    });
  }

  statusLabel(status: number | null): string {
    if (status === 0) return 'Ativa';
    if (status === 1) return 'Concluida';
    if (status === 2) return 'Cancelada';
    return '---';
  }

  voltar(): void {
    this.router.navigate(['/admin/matriculas']);
  }

  imprimir(): void {
    window.print();
  }

  async baixarPdf(): Promise<void> {
    if (!this.historico) return;
    this.gerandoPdf = true;
    this.changeDetectorRef.detectChanges();

    try {
      const el = document.getElementById('transcriptContent');
      if (!el) return;

      const canvas = await html2canvas(el, {
        scale: 3,
        useCORS: true,
        backgroundColor: '#ffffff',
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 10;
      const imgWidth = pageWidth - margin * 2;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      let heightLeft = imgHeight;
      let position = margin;

      pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
      heightLeft -= pageHeight - margin * 2;

      while (heightLeft > 0) {
        position = -(imgHeight - heightLeft) + margin;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight);
        heightLeft -= pageHeight - margin * 2;
      }

      const nome = this.historico.aluno.nome.replace(/\s+/g, '_');
      pdf.save(`historico_${nome}.pdf`);
    } catch {
      this.error = 'Erro ao gerar PDF. Tente usar Ctrl+P para imprimir.';
    } finally {
      this.gerandoPdf = false;
      this.changeDetectorRef.detectChanges();
    }
  }
}
