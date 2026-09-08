import { Injectable, signal } from '@angular/core';

export type NotificationType = 'error' | 'success';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  readonly message = signal<string | null>(null);
  readonly type = signal<NotificationType>('error');
  private timer: ReturnType<typeof setTimeout> | null = null;

  error(message: string, autoDismissMs = 10000): void {
    this.clearTimer();
    this.type.set('error');
    this.message.set(message);
    if (autoDismissMs > 0) {
      this.timer = setTimeout(() => this.clear(), autoDismissMs);
    }
  }

  success(message: string, autoDismissMs = 3000): void {
    this.clearTimer();
    this.type.set('success');
    this.message.set(message);
    if (autoDismissMs > 0) {
      this.timer = setTimeout(() => this.clear(), autoDismissMs);
    }
  }

  clear(): void {
    this.clearTimer();
    this.message.set(null);
  }

  private clearTimer(): void {
    if (this.timer !== null) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
}
