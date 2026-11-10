import { TestBed } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';
import { UsuarioFormComponent } from './usuario-form';

 describe('UsuarioForm review regressions', () => {
  function setup(edit = false, director = true) {
    const fixture = TestBed.createComponent(UsuarioFormComponent);
    const component = fixture.componentInstance;
    component.mode = edit ? 'edit' : 'create';
    component.canAssignDiretoria = director;
    component.existingEmails = ['taken@abaco.org.br'];
    component.usuario = edit ? {
      idUsuario: 1, nome: 'Dr. Joao', telefone: '1133334444',
      email: 'director@abaco.org.br', cargo: 1, endereco: 'Rua antiga',
    } : null;
    component.ngOnChanges({ mode: new SimpleChange(null, component.mode, true) });
    fixture.detectChanges();
    return { fixture, component };
  }

  it('preserves director role and blocks admin submission', () => {
    const { component } = setup(true, false);
    let saved = false;
    component.save.subscribe(() => saved = true);
    expect(component.form.controls.cargo.value).toBe(1);
    expect(component.roleOptions.some(option => option.value === 1)).toBe(false);
    expect(component.form.disabled).toBe(true);
    component.submit();
    expect(saved).toBe(false);
  });

  it('accepts institutional and gmail domains and shows duplicate email feedback', () => {
    const { fixture, component } = setup();
    const email = component.form.controls.email;

    email.setValue('user@gmail.com');
    email.markAsTouched();
    expect(email.hasError('institutionalEmail')).toBe(false);

    email.setValue('user@hotmail.com');
    email.markAsTouched();
    fixture.changeDetectorRef.markForCheck();
    fixture.detectChanges();
    expect(email.hasError('institutionalEmail')).toBe(true);
    expect(fixture.nativeElement.textContent).toContain('@gmail.com');
    email.setValue('TAKEN@abaco.org.br');
    fixture.changeDetectorRef.markForCheck();
    fixture.detectChanges();
    expect(email.hasError('emailTaken')).toBe(true);
    expect(fixture.nativeElement.textContent).toContain('ja esta cadastrado');
  });

  it('allows unchanged legacy name and phone but validates changed values', () => {
    const { component } = setup(true);
    expect(component.form.valid).toBe(true);
    let phone: string | null = null;
    component.save.subscribe(value => phone = value.telefone);
    component.submit();
    expect(phone).toBe('1133334444');
    component.form.controls.nome.setValue('---');
    expect(component.form.controls.nome.invalid).toBe(true);
    component.form.controls.telefone.setValue('123');
    expect(component.form.controls.telefone.invalid).toBe(true);
  });
});
