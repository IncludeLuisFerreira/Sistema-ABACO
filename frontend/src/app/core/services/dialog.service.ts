import { Injectable, inject, ApplicationRef, ComponentRef, EnvironmentInjector, createComponent } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { ConfirmDialog } from '../../shared/components/confirm-dialog/confirm-dialog';

export interface ConfirmOptions {
  title?: string;
  message: string;
  confirmLabel?: string;
  variant?: 'danger' | 'default';
}

@Injectable({ providedIn: 'root' })
export class DialogService {
  private readonly appRef = inject(ApplicationRef);
  private readonly injector = inject(EnvironmentInjector);

  confirm(options: ConfirmOptions): Observable<boolean> {
    const subject = new Subject<boolean>();

    const componentRef: ComponentRef<ConfirmDialog> = createComponent(ConfirmDialog, {
      environmentInjector: this.injector,
    });

    componentRef.instance.open = true;
    componentRef.instance.title = options.title || 'Confirmar ação';
    componentRef.instance.message = options.message;
    componentRef.instance.confirmLabel = options.confirmLabel || 'Confirmar';
    componentRef.instance.variant = options.variant || 'danger';

    componentRef.instance.confirm.subscribe(() => {
      subject.next(true);
      subject.complete();
      this.cleanup(componentRef);
    });

    componentRef.instance.closed.subscribe(() => {
      subject.next(false);
      subject.complete();
      this.cleanup(componentRef);
    });

    document.body.appendChild(componentRef.location.nativeElement);
    this.appRef.attachView(componentRef.hostView);

    return subject.asObservable();
  }

  private cleanup(ref: ComponentRef<ConfirmDialog>): void {
    setTimeout(() => {
      this.appRef.detachView(ref.hostView);
      ref.destroy();
    }, 150);
  }
}
