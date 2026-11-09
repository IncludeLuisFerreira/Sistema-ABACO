# Contexto do frontend

Leia junto com `CONTEXT.md` quando a tarefa tocar `frontend/`.

## Stack e estrutura

Angular 21.2 com **standalone components**, TypeScript 5.9 em modo `strict`, RxJS 7.8, SCSS por
componente, ApexCharts via `ng-apexcharts`, testes com Vitest 4 + jsdom.

```
frontend/src/app/
├── app.config.ts          # provideRouter + HttpClient com interceptors
├── app.routes.ts          # rotas raiz, lazy loading por feature
├── core/
│   ├── guards/            # authGuard, roleGuard(...), adminGuard
│   ├── interceptors/      # token.interceptor, error.interceptor
│   ├── models/            # interfaces TypeScript (*.model.ts)
│   ├── services/          # HTTP e estado (*.service.ts)
│   └── utils/             # api-error.ts
├── features/<dominio>/    # auth, dashboard, classes, students, courses, enrollments,
│   ├── pages/             #   attendance, grades, transcript, logistico, admin, errors
│   └── components/
└── shared/components/     # botões, campos, dialog, breadcrumb, etc.
```

Cada feature tem seu arquivo `<feature>.routes.ts`; o `app.routes.ts` carrega com `loadChildren`
ou `loadComponent`. Rotas internas usam `loadComponent`.

## Padrões obrigatórios

- Componente sempre `standalone: true`, com `imports: [...]` explícitos. Não use NgModule.
- Nomes de arquivo em kebab-case (`class-form.ts`, `turma-card.ts`); classe em PascalCase.
  O projeto mistura nomes em inglês e português — siga o diretório da feature.
- Estado local com propriedades e, quando reativo, **Signals**. Não introduza NgRx.
- `inject()` é aceitável em guards/interceptors; componentes existentes usam construtor. Siga o
  arquivo vizinho.
- Toda chamada HTTP fica em `core/services/<recurso>.service.ts`. O componente só se inscreve.
- Serviços usam caminho relativo (`private readonly baseUrl = '/api/v1/turmas'`), que o proxy de dev
  e o Nginx resolvem. O `auth.service.ts` usa o prefixo `environment.apiUrl`; siga o padrão do
  service que está editando, não misture os dois no mesmo arquivo.
- Erros de API são convertidos com `getApiErrorMessage(...)` de `core/utils/api-error.ts`.
  Feedback ao usuário via `NotificationService` e confirmação via `DialogService`.
- Rotas protegidas: `authGuard` para autenticação; `roleGuard([cargos])` para perfil;
  `adminGuard` (= `roleGuard([1, 3])`) para área administrativa. Professor é cargo `2`.
- `primeiro_acesso=true` redireciona para `/alterar-senha`.
- Estilo: SCSS do componente. **Não há Tailwind** — não use classes utilitárias.
- Formatação: Prettier com `printWidth: 100`, `singleQuote: true`, parser Angular para HTML.

## Receita: nova página em uma feature

1. Crie `features/<dominio>/pages/<nome>/<nome>.ts|.html|.scss`.
2. Componente standalone, com `templateUrl` e `styleUrls` (ou `styleUrl`) apontando para os arquivos.
3. Adicione a rota no `<dominio>.routes.ts` com `loadComponent` e os guards adequados.
4. Se precisar de dados, crie/estenda o service em `core/services/` e o model em `core/models/`.
5. Escreva `<nome>.spec.ts` com `TestBed`, cobrindo renderização e o comportamento principal.
6. Rode `npm test -- --watch=false` e `npm run build`.

## Receita: novo service HTTP

```ts
@Injectable({ providedIn: 'root' })
export class RecursoService {
  private readonly baseUrl = '/api/v1/recurso';

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Recurso[]> {
    return this.http.get<Recurso[]>(this.baseUrl);
  }
}
```

- Um método por operação, tipado com `Observable<T>`.
- Não faça `subscribe` dentro do service (exceto efeito colateral explícito, como os services de
  estoque já fazem; não propague esse padrão sem necessidade).
- Não guarde token manualmente: o `tokenInterceptor` injeta `Authorization` a partir de
  `localStorage['abaco_token']`.

## Testes

- Builder `@angular/build:unit-test`, setup em `src/test-setup.ts` (stubs de `ResizeObserver` e SVG
  para ApexCharts em jsdom).
- Arquivos `*.spec.ts` ao lado do código.
- Padrão: `TestBed.configureTestingModule({ imports: [Componente] })`, `createComponent`,
  `fixture.detectChanges()`.
- Para HTTP, use `provideHttpClientTesting()` / `HttpTestingController` quando precisar assertar
  requisição. Não chame a API real.
- Cobertura configurada para guards, `auth.service`, login e access-denied; não amplie o escopo de
  cobertura sem pedido.

```bash
cd frontend
npm test -- --watch=false
npm run test:coverage -- --watch=false
npm run build
```

## Armadilhas frequentes

1. **`HttpClient` no componente** — quebra o padrão e os testes. Vá para o service.
2. **`subscribe` sem ciclo de vida** — use `takeUntilDestroyed()` ou `async` pipe quando o
   componente puder ser destruído com requisição pendente.
3. **Rota sem guard** — toda rota de negócio precisa de `authGuard`; área restrita precisa de
   `roleGuard`. Testar acesso negado é parte da entrega.
4. **Tailwind** — não existe no projeto. Não adicione classes que não fazem nada.
5. **Tipos frouxos** — `strict` está ligado; não use `any` para calar o compilador. Prefira model
   em `core/models/`.
6. **Duplicar chamada de API em componente** — carregue uma vez no `ngOnInit` e derive o resto.
7. **Mudar `environment.apiUrl`** — o valor vazio é intencional para produção via Nginx.
8. **ngModule / CommonModule desnecessário** — em standalone, importe só o que usa; `CommonModule`
   é aceitável para diretivas, mas evite importar módulo inteiro por hábito.
9. **ApexCharts em teste** — sem os stubs de `test-setup.ts` o jsdom quebra; não remova.
10. **Nomes de rota** — rotas de professor usam `/academico/...`; admin usa `/admin/...`. Confira o
    arquivo de rotas antes de criar link.

## Definição de pronto (frontend)

- Componente/service standalone e tipado, sem `any` novo.
- Rota protegida com guard correto.
- `npm test -- --watch=false` verde.
- `npm run build` verde.
- Sem `console.log` e sem chamada HTTP fora de `core/services/`.
