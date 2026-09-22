import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';

import { UsuarioFormComponent, UsuarioFormSubmit } from './usuario-form';
import { Usuario } from '../../../../core/models/usuario.model';

describe('UsuarioFormComponent', () => {
  let component: UsuarioFormComponent;
  let fixture: ComponentFixture<UsuarioFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UsuarioFormComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(UsuarioFormComponent);
    component = fixture.componentInstance;
    component.mode = 'create';
    component.ngOnChanges({
      mode: new SimpleChange(null, 'create', true),
    });
    fixture.detectChanges();
  });

  it('should create component', () => {
    expect(component).toBeTruthy();
  });

  it('should start with invalid form when fields are empty', () => {
    expect(component.form.valid).toBeFalse();
    expect(component.form.controls.nome.valid).toBeFalse();
    expect(component.form.controls.email.valid).toBeFalse();
    expect(component.form.controls.telefone.valid).toBeFalse();
    expect(component.form.controls.endereco.valid).toBeFalse();
    expect(component.form.controls.senha.valid).toBeFalse();
  });

  it('should invalidate email if format is incorrect', () => {
    component.form.controls.email.setValue('email_sem_arroba');
    expect(component.form.controls.email.hasError('email')).toBeTrue();
  });

  it('should mark fields touched and not emit save when submitting invalid form', () => {
    let emittedPayload: UsuarioFormSubmit | undefined;
    component.save.subscribe((val) => (emittedPayload = val));

    component.submit();

    expect(emittedPayload).toBeUndefined();
    expect(component.form.controls.nome.touched).toBeTrue();
    expect(component.form.controls.telefone.touched).toBeTrue();
    expect(component.form.controls.endereco.touched).toBeTrue();
    expect(component.form.controls.email.touched).toBeTrue();
  });

  it('should emit save with all required fields when form is valid', () => {
    let emittedPayload: UsuarioFormSubmit | undefined;
    component.save.subscribe((val) => (emittedPayload = val));

    component.form.setValue({
      nome: ' Maria Souza ',
      email: 'maria@abaco.org.br',
      telefone: ' (11) 98888-7777 ',
      endereco: ' Rua das Palmeiras, 100 ',
      cargo: 2,
      senha: 'minhasenha',
    });

    expect(component.form.valid).toBeTrue();

    component.submit();

    expect(emittedPayload).toEqual({
      nome: 'Maria Souza',
      email: 'maria@abaco.org.br',
      telefone: '(11) 98888-7777',
      endereco: 'Rua das Palmeiras, 100',
      cargo: 2,
      senha: 'minhasenha',
    });
  });

  it('should patch existing data and not require password in edit mode', () => {
    const existingUser: Usuario = {
      idUsuario: 10,
      nome: 'Carlos Antunes',
      email: 'carlos@abaco.org.br',
      telefone: '11977776666',
      endereco: 'Av. Paulista, 1000',
      cargo: 3,
    };

    component.mode = 'edit';
    component.usuario = existingUser;
    component.ngOnChanges({
      mode: new SimpleChange('create', 'edit', false),
      usuario: new SimpleChange(null, existingUser, false),
    });
    fixture.detectChanges();

    expect(component.form.controls.nome.value).toBe('Carlos Antunes');
    expect(component.form.controls.telefone.value).toBe('11977776666');
    expect(component.form.controls.endereco.value).toBe('Av. Paulista, 1000');
    expect(component.form.controls.email.disabled).toBeTrue();
    expect(component.form.controls.senha.validator).toBeNull();
    expect(component.form.valid).toBeTrue();
  });
});
