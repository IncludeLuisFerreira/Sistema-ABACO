import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'ab-password-field',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './password-field.html',
  styleUrls: ['./password-field.scss']
})
export class PasswordField {
  @Input() control: any;
  @Input() label = 'Senha';
  @Input() placeholder = 'Senha';

  show = false;
  toggle() { this.show = !this.show; }

  /** Mensagem conforme o erro real do controle, não só "obrigatória". */
  get errorMessage(): string | null {
    const errors = this.control?.errors;
    if (!errors) return null;
    if (errors['required']) return 'Senha é obrigatória';
    if (errors['minlength']) {
      const minimo = errors['minlength'].requiredLength;
      return `A senha deve ter no mínimo ${minimo} caracteres`;
    }
    if (errors['pattern']) return 'A senha deve conter letras e números';
    return 'Senha inválida';
  }
}
