#!/usr/bin/env bash
# Testes automatizados do scripts/agent-preflight.sh. Não requer rede: monta
# repositórios git locais temporários.
#
# Uso:
#   ./scripts/test_agent_preflight.sh
#
# Cobre:
#   1. clone direto: --check limpo retorna 0 e --start cria a partir de origin/develop.
#   2. fetch malsucedido: --check e --start abortam com código não-zero e sem efeito.
#   3. fork atrasado + upstream atualizado: --check detecta o atraso e --start
#      cria a branch a partir de upstream/develop.

set -euo pipefail

export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com
export GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFLIGHT="$SCRIPTS_DIR/agent-preflight.sh"
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

PASS=0
FAIL=0

ok_test()   { printf '[ok]    %s\n' "$*"; PASS=$((PASS+1)); }
fail_test() { printf '[falhou] %s\n' "$*"; FAIL=$((FAIL+1)); }

# run <workdir> <args...> -> roda o preflight e guarda saída/exit em OUT/CODE.
run() {
  local workdir="$1"; shift
  set +e
  OUT="$( (cd "$workdir" && "$PREFLIGHT" "$@") 2>&1 )"
  CODE=$?
  set -e
}

assert_exit() {  # assert_exit <esperado> <desc>
  if [ "$CODE" -eq "$1" ]; then ok_test "$2"; else fail_test "$2 (esperado exit $1, obtido $CODE; saída: $OUT)"; fi
}

assert_contains() {  # assert_contains <texto> <desc>
  if printf '%s' "$OUT" | grep -qF -- "$1"; then ok_test "$2"; else fail_test "$2 (não encontrou '$1'; saída: $OUT)"; fi
}

# --- helpers de montagem -----------------------------------------------------

commit() {  # commit <dir> <arquivo> <mensagem>
  local dir="$1" file="$2" msg="$3"
  echo "$msg" > "$dir/$file"
  git -C "$dir" add "$file"
  git -C "$dir" commit -q -m "$msg"
}

make_repo() {  # make_repo <dir> <branch>
  mkdir -p "$1"
  git -C "$1" init -q
  git -C "$1" checkout -q -b "$2"
}

# --- cenário 1: clone direto ------------------------------------------------

main="$ROOT/main"
make_repo "$main" develop
commit "$main" a.txt "commit A"
A="$(git -C "$main" rev-parse develop)"

work="$ROOT/work"
git clone -q "$main" "$work"
git -C "$work" checkout -q -b feature/trabalho

run "$work" --check
assert_exit 0 "clone direto: --check limpo retorna 0"
assert_contains "Pronto para trabalhar." "clone direto: --check anuncia que está pronto"

# --start em clone direto cria a partir de origin/develop
work2="$ROOT/work2"
git clone -q "$main" "$work2"
run "$work2" --start feature/nova
assert_exit 0 "clone direto: --start retorna 0"
tip="$(git -C "$work2" rev-parse feature/nova 2>/dev/null || true)"
if [ "$tip" = "$A" ]; then ok_test "clone direto: --start cria a branch a partir de origin/develop"; else fail_test "clone direto: --start criou a branch de outra base (tip=$tip esperado=$A)"; fi

# --- cenário 2: fetch malsucedido -------------------------------------------

work3="$ROOT/work3"
git clone -q "$main" "$work3"
git -C "$work3" remote set-url origin "$ROOT/inexistente"

run "$work3" --check
assert_exit 1 "fetch falho: --check aborta com código não-zero"
assert_contains "Não foi possível executar 'git fetch" "fetch falho: --check reporta a falha"

run "$work3" --start feature/x
assert_exit 1 "fetch falho: --start aborta com código não-zero"
if [ -z "$(git -C "$work3" branch --list feature/x)" ]; then ok_test "fetch falho: --start não cria a branch"; else fail_test "fetch falho: --start criou a branch mesmo com fetch falho"; fi
if [ "$(git -C "$work3" symbolic-ref --short -q HEAD)" = "develop" ]; then ok_test "fetch falho: --start não troca de branch"; else fail_test "fetch falho: --start trocou de branch"; fi

# --- cenário 3: fork atrasado + upstream atualizado --------------------------

up="$ROOT/up"
make_repo "$up" develop
commit "$up" a.txt "commit A"
git clone -q --bare "$up" "$ROOT/fork.git"     # fork fica em A
commit "$up" b.txt "commit B"                    # upstream anda para B
B="$(git -C "$up" rev-parse develop)"
git clone -q --bare "$up" "$ROOT/upstream.git"   # upstream contém A..B

fork_work="$ROOT/fork_work"
git clone -q "$ROOT/fork.git" "$fork_work"
git -C "$fork_work" remote add upstream "$ROOT/upstream.git"
git -C "$fork_work" fetch -q upstream
git -C "$fork_work" checkout -q -b feature/base

run "$fork_work" --check
assert_exit 1 "fork atrasado: --check detecta o atraso via upstream"
assert_contains "atrás de upstream/develop" "fork atrasado: --check usa upstream/develop (não origin/develop)"

fork_work2="$ROOT/fork_work2"
git clone -q "$ROOT/fork.git" "$fork_work2"
git -C "$fork_work2" remote add upstream "$ROOT/upstream.git"
git -C "$fork_work2" fetch -q upstream
run "$fork_work2" --start feature/nova
tip2="$(git -C "$fork_work2" rev-parse feature/nova 2>/dev/null || true)"
if [ "$tip2" = "$B" ]; then ok_test "fork: --start cria a branch a partir de upstream/develop (commit mais recente)"; else fail_test "fork: --start criou de base errada (tip=$tip2 esperado=$B)"; fi

# --- resultado ---------------------------------------------------------------

echo ""
echo "Resultado: $PASS ok, $FAIL falha(s)"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
