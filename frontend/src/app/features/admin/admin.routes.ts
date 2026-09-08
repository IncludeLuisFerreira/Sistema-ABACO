import { Routes } from '@angular/router';
import { authGuard } from '../../core/guards/auth.guard';
import { adminGuard, directorGuard } from '../../core/guards/role.guard';

export const ADMIN_ROUTES: Routes = [
	{
		path: '',
		canActivate: [authGuard],
		loadComponent: () => import('./components/admin-layout/admin-layout').then(m => m.AdminLayoutComponent),
		children: [
			{ path: '', pathMatch: 'full', redirectTo: 'home' },
			{
				path: 'home',
				canActivate: [adminGuard],
				loadComponent: () => import('./pages/home/home').then(m => m.AdminHome)
			},
			{
				path: 'dashboard',
				canActivate: [directorGuard],
				redirectTo: 'home',
			},
			{
				path: 'usuarios',
				canActivate: [directorGuard],
				loadComponent: () =>
					import('../users/pages/users-management/users-management').then(m => m.UsersManagementComponent)
			},
			{
				path: 'alunos',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../students/pages/students-management/students-management').then(m => m.StudentsManagementComponent)
			},
			{
				path: 'cursos',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../courses/pages/courses-management/courses-management').then(m => m.CoursesManagementComponent)
			},
			{
				path: 'turmas',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../classes/pages/classes-management/classes-management').then(m => m.ClassesManagementComponent)
			},
			{
				path: 'matriculas',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../enrollments/pages/enrollments-management/enrollments-management').then(m => m.EnrollmentsManagementComponent)
			},
			{
				path: 'matriculas/:id/notas',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../grades/pages/student-grades/student-grades').then(m => m.StudentGradesComponent)
			},
			{
				path: 'historico/matricula/:id',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../transcript/pages/transcript-view/transcript-view').then(m => m.TranscriptViewComponent)
			},
			{
				path: 'presencas',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../attendance/pages/attendance-management/attendance-management').then(m => m.AttendanceManagementComponent)
			},
			{
				path: 'notas',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../grades/pages/grades-management/grades-management').then(m => m.GradesManagementComponent)
			},
			{
				path: 'notas/aluno/:id',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../grades/pages/student-grades/student-grades').then(m => m.StudentGradesComponent)
			},
			{
				path: 'logistico',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../logistico/pages/home/home').then(m => m.LogisticoHome)
			},
			{
				path: 'logistico/estoque',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../logistico/pages/estoque-management/estoque-management').then(m => m.EstoqueManagementComponent)
			},
			{
				path: 'logistico/pedidos',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../logistico/pages/pedido-list/pedido-list').then(m => m.PedidoListComponent)
			},
			{
				path: 'logistico/pedidos/novo',
				canActivate: [adminGuard],
				loadComponent: () =>
					import('../logistico/pages/pedido-form/pedido-form').then(m => m.PedidoFormPageComponent)
			}
		]
	}
];
