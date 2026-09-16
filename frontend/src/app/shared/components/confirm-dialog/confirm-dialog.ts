import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ab-confirm-dialog',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './confirm-dialog.html',
  styleUrls: ['./confirm-dialog.scss'],
})
export class ConfirmDialog {
  @Input() open = false;
  @Input() title = 'Confirmar ação';
  @Input() message = 'Tem certeza que deseja continuar?';
  @Input() confirmLabel = 'Confirmar';
  @Input() cancelLabel = 'Cancelar';
  @Input() variant: 'danger' | 'default' = 'danger';
  @Input() loading = false;

  @Output() confirm = new EventEmitter<void>();
  @Output() closed = new EventEmitter<void>();

  onConfirm(): void {
    if (this.loading) return;
    this.confirm.emit();
  }

  onCancel(): void {
    this.closed.emit();
  }
}
