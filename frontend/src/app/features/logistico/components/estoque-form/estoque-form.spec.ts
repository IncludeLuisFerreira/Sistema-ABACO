import { TestBed } from '@angular/core/testing';

import { EstoqueFormComponent, EstoqueFormSubmit } from './estoque-form';

describe('EstoqueFormComponent - validacao', () => {
  function setup() {
    const fixture = TestBed.createComponent(EstoqueFormComponent);
    fixture.detectChanges();
    return { fixture, component: fixture.componentInstance };
  }

  it('rejeita quantidade disponivel negativa', () => {
    const { component } = setup();

    component.form.controls.quantidadeDisponivel.setValue(-1);

    expect(component.form.controls.quantidadeDisponivel.hasError('min')).toBe(true);
    expect(component.form.invalid).toBe(true);
  });

  it('rejeita estoque minimo negativo', () => {
    const { component } = setup();

    component.form.controls.estoqueMinimo.setValue(-5);

    expect(component.form.controls.estoqueMinimo.hasError('min')).toBe(true);
  });

  it('aceita quantidade e estoque minimo zero', () => {
    const { component } = setup();

    component.form.controls.nomeItem.setValue('Caneta');
    component.form.controls.quantidadeDisponivel.setValue(0);
    component.form.controls.estoqueMinimo.setValue(0);

    expect(component.form.valid).toBe(true);
  });

  it('rejeita nome formado apenas por espacos', () => {
    const { component } = setup();

    component.form.controls.nomeItem.setValue('   ');

    expect(component.form.controls.nomeItem.hasError('pattern')).toBe(true);
  });

  it('emite nome sem espacos nas bordas', () => {
    const { component } = setup();
    const payloads: EstoqueFormSubmit[] = [];
    component.save.subscribe((value) => payloads.push(value));
    component.form.controls.nomeItem.setValue('  Caneta  ');

    component.submit();

    expect(payloads[0]?.nomeItem).toBe('Caneta');
  });

  it('emite cancelamento ao clicar no botao de fechar', () => {
    const { fixture, component } = setup();
    let cancelled = false;
    component.cancel.subscribe(() => (cancelled = true));

    const closeButton = fixture.nativeElement.querySelector('.close-btn') as HTMLButtonElement;
    closeButton.click();

    expect(cancelled).toBe(true);
  });
});
