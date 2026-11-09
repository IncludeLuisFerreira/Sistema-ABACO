#!/usr/bin/env bash
# Preflight para agentes e pessoas: garante que a branch de trabalho nasceu
# de uma origin/develop atualizada.
#
# Uso:
#   ./scripts/agent-preflight.sh --check
#   ./scripts/agent-preflight.sh --start feature/minha-feature
#
# Variáveis:
#   REMOTE=origin   (padrão)

set -euo pipefail

REMOTE="${REMOTE:-origin}"
MODE="check"
BRANCH_NAME=""
EXIT_CODE=0

usage() {
  cat <<'EOF'
Uso:
  ./scripts/agent-preflight.sh --check
      Verifica branch atual, working tree, atraso em relação a origin/develop e .env.

  ./scripts/agent-preflight.sh --start <tipo/nome>
      Cria uma branch nova a partir de origin/develop.
      Tipos aceitos: feature, fix, docs, refactor, test, chore.

  ./scripts/agent-preflight.sh --help
EOF
}

say()  { printf '%s\n' "$*"; }
ok()   { printf '[ok]    %s\n' "$*"; }
warn() { printf '[aviso] %s\n' "$*"; }
fail() { printf '[erro]  %s\n' "$*"; EXIT_CODE=1; }

require_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    say "Este comando precisa ser executado dentro do repositório."
    exit 2
  fi
}

require_remote() {
  if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
    say "Remote '$REMOTE' não encontrado. Configure com: git remote add $REMOTE <url>"
    exit 2
  fi
}

update_remote() {
  if git fetch "$REMOTE" --prune >/dev/null 2>&1; then
    ok "Referências de $REMOTE atualizadas."
  else
    warn "Não foi possível executar 'git fetch $REMOTE'. Verifique rede/credenciais."
    warn "A verificação de atraso pode estar desatualizada."
  fi
}

require_develop_ref() {
  if ! git rev-parse --verify --quiet "$REMOTE/develop" >/dev/null; then
    say "A referência '$REMOTE/develop' não existe. Rode: git fetch $REMOTE --prune"
    exit 2
  fi
}

current_branch() {
  git symbolic-ref --short -q HEAD || true
}

dirty_files() {
  git status --porcelain
}

validate_branch_name() {
  local name="$1"
  if ! printf '%s' "$name" | grep -Eq '^(feature|fix|docs|refactor|test|chore)/[a-z0-9][a-z0-9._-]*$'; then
    say "Nome de branch inválido: '$name'"
    say "Use tipo/slug em kebab-case. Ex.: feature/relatorio-frequencia"
    say "Tipos aceitos: feature, fix, docs, refactor, test, chore."
    exit 2
  fi
}

check_mode() {
  local branch
  branch="$(current_branch)"

  if [ -z "$branch" ]; then
    fail "HEAD destacado (detached). Crie ou entre em uma branch antes de trabalhar."
  else
    ok "Branch atual: $branch"
    case "$branch" in
      main|develop)
        fail "Você está em '$branch'. Não faça alterações diretas nessa branch."
        ;;
    esac
  fi

  local dirty
  dirty="$(dirty_files)"
  if [ -z "$dirty" ]; then
    ok "Working tree limpa."
  else
    fail "Há mudanças não commitadas:"
    printf '%s\n' "$dirty" | sed 's/^/        /'
    say "        Commit ou stash antes de trocar de base; não faça pull com a árvore suja."
  fi

  require_develop_ref

  local behind ahead
  behind="$(git rev-list --count "HEAD..$REMOTE/develop" 2>/dev/null || true)"
  ahead="$(git rev-list --count "$REMOTE/develop..HEAD" 2>/dev/null || true)"

  if [ "${behind:-0}" -gt 0 ] 2>/dev/null; then
    fail "Sua branch está $behind commit(s) atrás de $REMOTE/develop."
    say "        Atualize antes de continuar: git rebase $REMOTE/develop"
    say "        Commits que faltam:"
    git log --oneline "HEAD..$REMOTE/develop" | sed 's/^/        /'
  else
    ok "Branch contém $REMOTE/develop (nenhum commit atrasado)."
  fi

  if [ "${ahead:-0}" -gt 0 ] 2>/dev/null; then
    say "        Commits só nesta branch: $ahead"
  fi

  if [ -f .env ]; then
    ok ".env presente."
  else
    warn ".env ausente. Copie de .env.example antes de subir a stack."
  fi

  say ""
  if [ "$EXIT_CODE" -eq 0 ]; then
    say "Pronto para trabalhar."
  else
    say "Corrija os itens marcados como [erro] antes de começar."
  fi
}

start_mode() {
  validate_branch_name "$BRANCH_NAME"
  update_remote
  require_develop_ref

  local head
  head="$(git rev-parse --verify --quiet "refs/heads/$BRANCH_NAME" || true)"
  if [ -n "$head" ]; then
    say "A branch '$BRANCH_NAME' já existe localmente. Entre nela ou escolha outro nome."
    exit 2
  fi

  local remote_head
  remote_head="$(git rev-parse --verify --quiet "refs/remotes/$REMOTE/$BRANCH_NAME" || true)"
  if [ -n "$remote_head" ]; then
    say "A branch '$BRANCH_NAME' já existe em $REMOTE. Use outro nome ou faça fetch/checkout dela."
    exit 2
  fi

  if [ -n "$(dirty_files)" ]; then
    say "Working tree suja. Commit ou stash antes de criar a branch:"
    dirty_files | sed 's/^/        /'
    exit 1
  fi

  git switch --no-track -c "$BRANCH_NAME" "$REMOTE/develop" >/dev/null
  ok "Branch '$BRANCH_NAME' criada a partir de $REMOTE/develop."
  say "        Base: $(git log -1 --oneline "$REMOTE/develop")"
  say ""
  say "Próximos passos:"
  say "  1. Implemente e escreva os testes."
  say "  2. Rode ./scripts/agent-preflight.sh --check antes do PR."
  say "  3. Publique com: git push -u origin $BRANCH_NAME"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --check)
      MODE="check"
      shift
      ;;
    --start)
      if [ $# -lt 2 ]; then
        say "Faltou o nome da branch após --start."
        usage
        exit 2
      fi
      MODE="start"
      BRANCH_NAME="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      say "Opção desconhecida: $1"
      usage
      exit 2
      ;;
  esac
done

require_git_repo
require_remote

if [ "$MODE" = "start" ]; then
  start_mode
else
  update_remote
  check_mode
fi

exit "$EXIT_CODE"
