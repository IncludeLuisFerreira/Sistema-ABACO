import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'ab-email-field',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './email-field.html',
  styleUrls: ['./email-field.scss']
})
export class EmailField {
  @Input() control: any;
  @Input() label = 'E-mail';
  @Input() placeholder = 'Digite seu e-mail';
}
