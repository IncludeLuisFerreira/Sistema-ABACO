import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { UsersManagementComponent } from './users-management';
import { UsuarioService } from '../../../../core/services/usuario.service';
import { AuthService } from '../../../../core/services/auth.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { DialogService } from '../../../../core/services/dialog.service';
import { CargoNivel } from '../../../../core/models/usuario.model';

 describe('UsersManagement review regressions', () => {
  const user = { idUsuario: 1, nome: 'Diretora', telefone: '', email: 'user@abaco.org.br', cargo: 1 as const };
  function setup(role = 'DIRECTOR') {
    const messages: string[] = [];
    const update = vi.fn(() => throwError(() => new HttpErrorResponse({ status: 422, error: { detail: [{ msg: 'Nome invalido' }] } })));
    TestBed.configureTestingModule({ providers: [
      { provide: UsuarioService, useValue: {
        list: () => of([{ ...user, email: null }]),
        update,
      } },
      { provide: AuthService, useValue: { getRoleFromToken: () => role } },
      { provide: DialogService, useValue: {} },
      { provide: NotificationService, useValue: { error: (message: string) => messages.push(message) } },
    ] });
    const fixture = TestBed.createComponent(UsersManagementComponent);
    const component = fixture.componentInstance;
    component.ngOnInit();
    return { component, messages, update };
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

  it('bloqueia cargo inválido sem chamar a API', () => {
    const { component, messages, update } = setup();
    component.openEdit(user);
    component.onSave({
      nome: 'Diretora',
      telefone: null,
      email: user.email,
      cargo: 4 as CargoNivel,
    });

    expect(messages).toEqual([
      'Nível de acesso inválido. Selecione Diretoria, Professor ou Admin.',
    ]);
    expect(update).not.toHaveBeenCalled();
    expect(component.saving).toBe(false);
  });
});
