import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'ab-password-field',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './password-field.html',
  styleUrls: ['./password-field.scss'],
})
export class PasswordField {
  @Input() control: any;
  @Input() label = 'Senha';
  @Input() placeholder = 'Senha';

  show = false;
  toggle() {
    this.show = !this.show;
  }

  /** Id estável por campo, usado para associar label, input e mensagem de erro. */
  get fieldId(): string {
    const suffix =
      this.control?.id ||
      this.label
        .toLowerCase()
        .normalize('NFD')
        .replace(/[^a-z0-9]+/g, '-');
    return `pwd-${suffix}`;
  }

  /** Mensagem conforme o erro real do controle, não só "obrigatória". */
  get errorMessage(): string | null {
    const errors = this.control?.errors;
    if (!errors) return null;
    if (errors['required']) return 'Senha é obrigatória';
    if (errors['minlength']) {
      const minimo = errors['minlength'].requiredLength;
      const unidade = minimo === 1 ? 'caractere' : 'caracteres';
      return `A senha deve ter no mínimo ${minimo} ${unidade}`;
    }
    if (errors['passwordComposition']) return 'A senha deve conter letras e números';
    return 'Senha inválida';
  }

  /** Exibe o erro depois que o usuário interagiu (digitou ou saiu do campo). */
  get showError(): boolean {
    if (!this.errorMessage) return false;
    return !!(this.control?.dirty || this.control?.touched);
  }
}
