// Polyfills necessários para testes com jsdom que renderizam libs de gráfico (apexcharts).
if (!(globalThis as unknown as { ResizeObserver?: unknown }).ResizeObserver) {
  class ResizeObserverStub {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  }

  (globalThis as unknown as { ResizeObserver: unknown }).ResizeObserver = ResizeObserverStub;
}

// jsdom não implementa getBBox/getScreenCTM, usados pelo apexcharts ao renderizar SVG.
// Os stubs abaixo só são aplicados quando a API está ausente, para não mascarar
// comportamento real de um navegador que já a implemente.
if (typeof SVGElement !== 'undefined') {
  const proto = SVGElement.prototype as unknown as {
    getBBox?: () => unknown;
    getScreenCTM?: () => unknown;
  };
  if (!proto.getBBox) {
    proto.getBBox = () => ({ x: 0, y: 0, width: 0, height: 0 });
  }
  if (!proto.getScreenCTM) {
    proto.getScreenCTM = () => null;
  }
}
