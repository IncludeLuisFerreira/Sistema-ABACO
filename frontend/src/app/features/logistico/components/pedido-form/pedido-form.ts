import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnDestroy, OnInit, Output, inject } from '@angular/core';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Subject, Subscription, debounceTime, distinctUntilChanged, switchMap } from 'rxjs';

import { AuthService } from '../../../../core/services/auth.service';
import { Estoque } from '../../../../core/models/estoque.model';
import { EstoqueService } from '../../../../core/services/estoque.service';
import { Turma } from '../../../../core/models/turma.model';
import { TurmaService } from '../../../../core/services/turma.service';

export interface PedidoFormSubmit {
  idTurma: number;
  dataPedido: string | null;
  itens: { nomeItem: string; quantidade: number | null; idItemEstoque: number | null }[];
}

@Component({
  selector: 'app-pedido-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './pedido-form.html',
  styleUrls: ['./pedido-form.scss'],
})
export class PedidoFormComponent implements OnInit, OnDestroy {
  private readonly subscriptions: Subscription[] = [];
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly estoqueService = inject(EstoqueService);
  private readonly turmaService = inject(TurmaService);

  @Input() loading = false;

  @Output() readonly save = new EventEmitter<PedidoFormSubmit>();
  @Output() readonly cancel = new EventEmitter<void>();

  turmas: Turma[] = [];
  estoqueItems: Estoque[] = [];
  filteredEstoque: Estoque[][] = [];
  searchTerms: Subject<string>[] = [];
  showDropdown: boolean[] = [];
  private searchInputValues: string[] = [];

  readonly form = this.fb.nonNullable.group({
    idTurma: [<number | null>null, [Validators.required]],
    dataPedido: [''],
    itens: this.fb.nonNullable.array([
      this.createItemGroup(),
    ]),
  });

  ngOnInit(): void {
    this.loadTurmas();
    this.loadEstoque();
    setTimeout(() => this.searchTerms.forEach((_, i) => this.setupSearch(i)));
  }

  get itensArray(): FormArray {
    return this.form.controls.itens;
  }

  addItem(): void {
    this.itensArray.push(this.createItemGroup());
    const idx = this.searchTerms.length - 1;
    this.setupSearch(idx);
  }

  removeItem(index: number): void {
    if (this.itensArray.length > 1) {
      this.itensArray.removeAt(index);
      this.filteredEstoque.splice(index, 1);
      this.showDropdown.splice(index, 1);
      this.searchTerms.splice(index, 1);
      this.searchInputValues.splice(index, 1);
    }
  }

  onSearchInput(index: number, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searchInputValues[index] = value;

    const group = this.itensArray.at(index);
    group.patchValue({ nomeItem: value });

    if (this.searchTerms[index]) {
      this.searchTerms[index].next(value);
    }
  }

  selectItem(index: number, item: Estoque): void {
    const group = this.itensArray.at(index);
    group.patchValue({
      idItemEstoque: item.idItemEstoque,
      nomeItem: item.nomeItem,
    });
    this.showDropdown[index] = false;

    this.searchInputValues[index] = item.nomeItem ?? '';
  }

  hasFilteredItems(index: number): boolean {
    return (this.filteredEstoque[index]?.length ?? 0) > 0;
  }

  onFocus(index: number): void {
    this.showDropdown[index] = true;
  }

  onBlur(index: number): void {
    setTimeout(() => {
      this.showDropdown[index] = false;
    }, 200);
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const payload: PedidoFormSubmit = {
      idTurma: value.idTurma!,
      dataPedido: value.dataPedido || null,
      itens: value.itens.map((item) => ({
        nomeItem: item.nomeItem ?? '',
        quantidade: item.quantidade ?? null,
        idItemEstoque: item.idItemEstoque ?? null,
      })),
    };

    this.save.emit(payload);
  }

  private createItemGroup() {
    this.filteredEstoque.push([]);
    this.showDropdown.push(false);
    this.searchTerms.push(new Subject<string>());
    this.searchInputValues.push('');
    return this.fb.nonNullable.group({
      nomeItem: ['', [Validators.required]],
      idItemEstoque: [<number | null>null],
      quantidade: [<number | null>null],
    });
  }

  private setupSearch(index: number): void {
    const sub = this.searchTerms[index].pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap((term) => {
        if (!term || term.trim().length === 0) {
          return [this.estoqueItems];
        }
        return this.estoqueService.search(term);
      }),
    ).subscribe((items) => {
      this.filteredEstoque[index] = items;
    });
    this.subscriptions.push(sub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((s) => s.unsubscribe());
    this.subscriptions.length = 0;
    this.searchTerms.forEach((s) => s.complete());
  }

  private loadTurmas(): void {
    const role = this.authService.getRoleFromToken();
    const obs = role === 'TEACHER' ? this.turmaService.listMine() : this.turmaService.list();
    const sub = obs.subscribe({
      next: (turmas) => {
        this.turmas = turmas;
      },
      error: () => {},
    });
    this.subscriptions.push(sub);
  }

  private loadEstoque(): void {
    const sub = this.estoqueService.list().subscribe({
      next: (items) => {
        this.estoqueItems = items;
        this.filteredEstoque = this.filteredEstoque.map(() => [...items]);
      },
      error: () => {},
    });
    this.subscriptions.push(sub);
  }
}
