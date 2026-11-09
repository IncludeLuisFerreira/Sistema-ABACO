import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { UsersManagementComponent } from './users-management';
import { UsuarioService } from '../../../../core/services/usuario.service';
import { AuthService } from '../../../../core/services/auth.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { DialogService } from '../../../../core/services/dialog.service';

 describe('UsersManagement review regressions', () => {
  const user = { idUsuario: 1, nome: 'Diretora', telefone: '', email: 'user@abaco.org.br', cargo: 1 as const };
  function setup(role = 'DIRECTOR') {
    const messages: string[] = [];
    TestBed.configureTestingModule({ providers: [
      { provide: UsuarioService, useValue: {
        list: () => of([{ ...user, email: null }]),
        update: () => throwError(() => new HttpErrorResponse({ status: 422, error: { detail: [{ msg: 'Nome invalido' }] } })),
      } },
      { provide: AuthService, useValue: { getRoleFromToken: () => role } },
      { provide: DialogService, useValue: {} },
      { provide: NotificationService, useValue: { error: (message: string) => messages.push(message) } },
    ] });
    const fixture = TestBed.createComponent(UsersManagementComponent);
    const component = fixture.componentInstance;
    component.ngOnInit();
    return { component, messages };
  }
  it('blocks admin opening a director record', () => {
    const { component } = setup('ADMIN');
    component.openEdit(user);
    expect(component.panelOpen).toBe(false);
  });
  it('extracts update validation messages and handles null email', () => {
    const { component, messages } = setup();
    expect(component.existingEmails).toEqual([]);
    component.onSearch('diretora');
    expect(component.filteredUsuarios.length).toBe(1);
    component.openEdit(user);
    component.onSave({ nome: '---', telefone: null, email: user.email, cargo: 1 });
    expect(messages).toEqual(['Nome invalido']);
    expect(component.saving).toBe(false);
  });
});
