import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PrimaryButton } from './primary-button';

describe('PrimaryButton', () => {
	let fixture: ComponentFixture<PrimaryButton>;

	beforeEach(async () => {
		await TestBed.configureTestingModule({ imports: [PrimaryButton] }).compileComponents();
		fixture = TestBed.createComponent(PrimaryButton);
		fixture.componentRef.setInput('label', 'Salvar');
		fixture.detectChanges();
	});

	it('renders the configured label', () => {
		expect(fixture.nativeElement.textContent).toContain('Salvar');
	});
});