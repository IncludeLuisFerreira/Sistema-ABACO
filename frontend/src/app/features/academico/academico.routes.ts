import { Routes } from '@angular/router';
import { authGuard } from '../../core/guards/auth.guard';
import { roleGuard } from '../../core/guards/role.guard';
// REFACTOR: AcademicoLayoutComponent importado eagerly (os filhos são lazy)
import { AcademicoLayoutComponent } from './components/academico-layout/academico-layout';

export const ACADEMICO_ROUTES: Routes = [
	{
		path: '',
		canActivate: [authGuard, roleGuard([2])],
		component: AcademicoLayoutComponent,
		children: [
			{ path: '', pathMatch: 'full', loadComponent: () => import('./pages/home/home').then(m => m.AcademicoHome) },
			{ path: 'turmas', loadComponent: () => import('./pages/turmas/turmas').then(m => m.TurmasPage) },
			{ path: 'turmas/:id', loadComponent: () => import('./pages/turma-detail/turma-detail').then(m => m.TurmaDetailPage) },
			{ path: 'alunos', loadComponent: () => import('./pages/alunos/alunos').then(m => m.AlunosPage) },
			{ path: 'presencas', loadComponent: () => import('./pages/presencas/presencas').then(m => m.PresencasPage) },
			{ path: 'notas', loadComponent: () => import('./pages/notas/notas').then(m => m.NotasPage) },
			{ path: 'pedidos/novo', loadComponent: () => import('../logistico/pages/pedido-form/pedido-form').then(m => m.PedidoFormPageComponent) },
			{ path: 'pedidos', loadComponent: () => import('../logistico/pages/pedido-list/pedido-list').then(m => m.PedidoListComponent) },
		]
	}
];
