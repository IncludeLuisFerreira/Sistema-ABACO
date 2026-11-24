import { Routes } from '@angular/router';
import { authGuard } from '../../core/guards/auth.guard';
import { adminGuard } from '../../core/guards/role.guard';

export const ADMIN_ROUTES: Routes = [
	{
		// O guard no nó pai cobre todos os filhos (Diretoria e Admin).
		path: '',
		canActivate: [authGuard, adminGuard],
		loadComponent: () => import('./components/admin-layout/admin-layout').then(m => m.AdminLayoutComponent),
		children: [
			{ path: '', pathMatch: 'full', redirectTo: 'home' },
			{
				path: 'home',
				loadComponent: () => import('./pages/home/home').then(m => m.AdminHome)
			},
			{
				// REFACTOR: rota 'dashboard' apenas redireciona para 'home'
				path: 'dashboard',
				redirectTo: 'home',
			},
			{
				path: 'usuarios',
				loadComponent: () =>
					import('../users/pages/users-management/users-management').then(m => m.UsersManagementComponent)
			},
			{
				path: 'alunos',
				loadComponent: () =>
					import('../students/pages/students-management/students-management').then(m => m.StudentsManagementComponent)
			},
			{
				path: 'cursos',
				loadComponent: () =>
					import('../courses/pages/courses-management/courses-management').then(m => m.CoursesManagementComponent)
			},
			{
				path: 'turmas',
				loadComponent: () =>
					import('../classes/pages/classes-management/classes-management').then(m => m.ClassesManagementComponent)
			},
			{
				path: 'matriculas',
				loadComponent: () =>
					import('../enrollments/pages/enrollments-management/enrollments-management').then(m => m.EnrollmentsManagementComponent)
			},
			{
				path: 'matriculas/:id/notas',
				loadComponent: () =>
					import('../grades/pages/student-grades/student-grades').then(m => m.StudentGradesComponent)
			},
			{
				path: 'historico/matricula/:id',
				loadComponent: () =>
					import('../transcript/pages/transcript-view/transcript-view').then(m => m.TranscriptViewComponent)
			},
			{
				path: 'presencas',
				loadComponent: () =>
					import('../attendance/pages/attendance-management/attendance-management').then(m => m.AttendanceManagementComponent)
			},
			{
				path: 'notas',
				loadComponent: () =>
					import('../grades/pages/grades-management/grades-management').then(m => m.GradesManagementComponent)
			},
			{
				path: 'notas/aluno/:id',
				loadComponent: () =>
					import('../grades/pages/student-grades/student-grades').then(m => m.StudentGradesComponent)
			},
			{
				path: 'logistico',
				loadComponent: () =>
					import('../logistico/pages/home/home').then(m => m.LogisticoHome)
			},
			{
				path: 'logistico/estoque',
				loadComponent: () =>
					import('../logistico/pages/estoque-management/estoque-management').then(m => m.EstoqueManagementComponent)
			},
			{
				path: 'logistico/pedidos',
				loadComponent: () =>
					import('../logistico/pages/pedido-list/pedido-list').then(m => m.PedidoListComponent)
			},
			{
				path: 'logistico/pedidos/novo',
				loadComponent: () =>
					import('../logistico/pages/pedido-form/pedido-form').then(m => m.PedidoFormPageComponent)
			}
		]
	}
];
