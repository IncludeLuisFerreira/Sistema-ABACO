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
}
