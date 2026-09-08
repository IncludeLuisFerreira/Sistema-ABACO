import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ab-primary-button',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './primary-button.html',
  styleUrls: ['./primary-button.scss']
})
export class PrimaryButton {
  @Input() disabled = false;
  @Input() label = 'Entrar';
}
