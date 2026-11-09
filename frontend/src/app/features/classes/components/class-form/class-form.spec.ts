import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Turma } from '../../../../core/models/turma.model';
import { ClassFormComponent, ClassFormSubmit } from './class-form';

const turmaExistente: Turma = {
  idTurma: 10,
  capacidade: 25,
  dataInicio: '2026-03-01',
  dataFim: '2026-06-30',
  idCurso: 1,
  idProfessor: 2,
  diasAula: '1,3',
  vagasOcupadas: 4,
  avaliacoes: [{ nome: 'Prova 1', tipo: 'prova', peso: 10 }],
  curso: { idCurso: 1, nomeCurso: 'Curso Teste' },
  professor: { idUsuario: 2, nome: 'Professor Teste' },
};

describe('ClassFormComponent', () => {
  let component: ClassFormComponent;
  let fixture: ComponentFixture<ClassFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClassFormComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ClassFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  function preencherFormularioValido(): void {
    component.form.patchValue({
      idCurso: 1,
      idProfessor: 2,
      capacidade: 20,
      dataInicio: '2026-03-01',
      dataFim: '2026-06-30',
    });
    component.diasAulaArray.patchValue([false, true, false, true, false, false, false]);
  }

  function capturarEnvios(): ClassFormSubmit[] {
    const envios: ClassFormSubmit[] = [];
    component.save.subscribe((payload) => envios.push(payload));
    return envios;
  }

  it('não emite quando campos obrigatórios estão vazios', () => {
    const envios = capturarEnvios();

    component.submit();

    expect(envios).toHaveLength(0);
    expect(component.form.controls.idCurso.touched).toBe(true);
  });

  it('não emite quando data fim é anterior à data início', () => {
    const envios = capturarEnvios();
    preencherFormularioValido();
    component.form.controls.dataFim.setValue('2026-02-01');

    component.submit();

    expect(envios).toHaveLength(0);
    expect(component.form.hasError('dateRange')).toBe(true);
  });

  it('não emite quando nenhum dia de aula é selecionado', () => {
    const envios = capturarEnvios();
    preencherFormularioValido();
    component.diasAulaArray.patchValue([false, false, false, false, false, false, false]);

    component.submit();

    expect(envios).toHaveLength(0);
    expect(component.diasAulaArray.hasError('atLeastOneDay')).toBe(true);
  });

  it('não emite quando avaliação tem peso inválido', () => {
    const envios = capturarEnvios();
    preencherFormularioValido();
    component.addAvaliacao();
    component.avaliacoesArray.at(0).patchValue({ nome: 'Prova 1', tipo: 'prova', peso: 0 });

    component.submit();

    expect(envios).toHaveLength(0);
  });

  it('emite payload válido sem converter obrigatórios para null', () => {
    const envios = capturarEnvios();
    preencherFormularioValido();

    component.submit();

    expect(envios).toHaveLength(1);
    expect(envios[0].idCurso).toBe(1);
    expect(envios[0].idProfessor).toBe(2);
    expect(envios[0].capacidade).toBe(20);
    expect(envios[0].dataInicio).toBe('2026-03-01');
    expect(envios[0].dataFim).toBe('2026-06-30');
    expect(envios[0].diasAula).toBe('1,3');
  });

  it('cria sem avaliações enviando null', () => {
    const envios = capturarEnvios();
    preencherFormularioValido();

    component.submit();

    expect(envios[0].avaliacoes).toBeNull();
  });

  it('edita sem avaliações enviando lista vazia para limpar', () => {
    const envios = capturarEnvios();
    component.mode = 'edit';
    preencherFormularioValido();

    component.submit();

    expect(envios[0].avaliacoes).toEqual([]);
  });

  it('duplica dados da turma, limpando as datas', () => {
    fixture.componentRef.setInput('mode', 'create');
    fixture.componentRef.setInput('turma', turmaExistente);
    fixture.componentRef.setInput('duplicate', true);
    fixture.detectChanges();

    expect(component.form.controls.idCurso.value).toBe(1);
    expect(component.form.controls.idProfessor.value).toBe(2);
    expect(component.form.controls.capacidade.value).toBe(25);
    expect(component.form.controls.dataInicio.value).toBe('');
    expect(component.form.controls.dataFim.value).toBe('');
    expect(component.diasAulaString).toBe('1,3');
    expect(component.avaliacoesArray.length).toBe(1);
  });

  it('recalcula o conflito quando as datas mudam', () => {
    fixture.componentRef.setInput('allTurmas', [turmaExistente]);
    fixture.detectChanges();
    component.form.patchValue({
      idCurso: 1,
      idProfessor: 2,
      capacidade: 20,
      dataInicio: '2026-04-01',
      dataFim: '2026-05-01',
    });
    component.diasAulaArray.patchValue([false, true, false, true, false, false, false]);

    component.updateContexto();
    expect(component.conflitoLabel).toContain('já tem');

    component.form.controls.dataInicio.setValue('2026-08-01');
    component.form.controls.dataFim.setValue('2026-09-01');
    component.updateContexto();

    expect(component.conflitoLabel).toBeNull();
  });
});
