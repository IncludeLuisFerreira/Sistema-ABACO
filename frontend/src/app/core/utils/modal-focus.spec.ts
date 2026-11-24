import { trapFocus } from './modal-focus';

describe('trapFocus', () => {
  function buildContainer(html: string): HTMLElement {
    const container = document.createElement('div');
    container.innerHTML = html;
    document.body.appendChild(container);
    return container;
  }

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('mantém Tab no card focado', () => {
    const container = buildContainer(`
      <div tabindex="-1" id="card">
        <button id="first">Primeiro</button>
        <button id="last">Último</button>
      </div>
    `);
    const card = container.querySelector('#card') as HTMLElement;
    card.focus();

    trapFocus(new KeyboardEvent('keydown', { key: 'Tab' }), container);

    expect(document.activeElement).toBe(card);
  });

  it('do último focável volta para o primeiro', () => {
    const container = buildContainer(`
      <button id="first">Primeiro</button>
      <button id="last">Último</button>
    `);
    const first = container.querySelector('#first') as HTMLElement;
    const last = container.querySelector('#last') as HTMLElement;
    last.focus();

    const event = new KeyboardEvent('keydown', { key: 'Tab', cancelable: true });
    trapFocus(event, container);

    expect(document.activeElement).toBe(first);
    expect(event.defaultPrevented).toBe(true);
  });

  it('Shift+Tab do primeiro vai para o último', () => {
    const container = buildContainer(`
      <button id="first">Primeiro</button>
      <button id="last">Último</button>
    `);
    const first = container.querySelector('#first') as HTMLElement;
    const last = container.querySelector('#last') as HTMLElement;
    first.focus();

    const event = new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, cancelable: true });
    trapFocus(event, container);

    expect(document.activeElement).toBe(last);
    expect(event.defaultPrevented).toBe(true);
  });

  it('ignora outras teclas e container nulo', () => {
    const container = buildContainer('<button id="first">Primeiro</button>');

    expect(() =>
      trapFocus(new KeyboardEvent('keydown', { key: 'Escape' }), container),
    ).not.toThrow();
    expect(() => trapFocus(new KeyboardEvent('keydown', { key: 'Tab' }), null)).not.toThrow();
  });

  it('não move o foco quando o card está vazio', () => {
    const container = buildContainer('<div id="card" tabindex="-1"></div>');
    const card = container.querySelector('#card') as HTMLElement;
    card.focus();

    const event = new KeyboardEvent('keydown', { key: 'Tab', cancelable: true });
    trapFocus(event, container);

    expect(document.activeElement).toBe(card);
    expect(event.defaultPrevented).toBe(true);
  });
});
