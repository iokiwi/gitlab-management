#!/usr/bin/env bash

function usage() {
cat << EOF
GitFlood - A script for running gitleaks across many repos at once.

usage: git-flood.sh [--h] [mode] [OPTIONS]

arguments:

  mode: The git leaks subcommand to run {dir,git}. Per the gitleaks docs:
    dir         scan directories or files for secrets
    git         scan git repositories for secrets

optional arguments:
    --clean            Delete the repos/ directory and reclone everyting
    --redact           {true,false,both}
    -h,--help          Show this help screen and exit.
EOF
}

ROOT_PATH="$(git rev-parse --show-toplevel)/scripts/gitflood"
REPOS_PATH="$ROOT_PATH/repos"
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --unredacted)
        DO_UNREDACTED="true"
        shift # past value
        ;;
    --redacted)
        DO_REDACTED="true"
        shift # past value
        ;;
    --clean)
        DO_CLEAN=true
        shift # past argument
        ;;
    -h|-help|--help|--h|help)
        usage;
        exit 0;
        ;;
    -*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

GITLEAKS_MODE=${1:-"git"} # To scan the entire git history, can do 'dir'

if [ -z "${GITLEAKS_MODE}" ]; then
    echo "Mode must be set to one of {git,dir}"
    usage; exit 1
fi

# List and clone repos

if [ "$DO_CLEAN" == "true" ]; then

    echo "Deleting $ROOT_PATH/results.."
    echo "Deleting $ROOT_PATH/repos..."

    rm -rf "$ROOT_PATH/results/" "$REPOS_PATH"
    mkdir -p "$REPOS_PATH"

    echo "Listing repos..."
    # shellcheck disable=SC2207
    ssh_urls=($(uv run gitlab-ls.py))

    cd "$REPOS_PATH" || exit 1;

    echo "Cloning repos into $REPOS_PATH..."
    for u in "${ssh_urls[@]}"; do
        git clone "$u"
    done

    cd "$ROOT_PATH" || exit 0;
fi


do_gitleaks() {

    repo_name=$1
    GITLEAKS_ARGS=$2

    cd "${REPOS_PATH}/${repo_name}" || exit 1

    mkdir -p "$RESULTS_PATH"
    gitleaks "$GITLEAKS_MODE" "$GITLEAKS_ARGS" \
        --report-path "$RESULTS_PATH/gitleaks_output_$repo_name.json"

    echo "# $repo_name" >> "$RESULTS_PATH/combined.json"
    cat "$RESULTS_PATH/gitleaks_output_$repo_name.json" >> "$RESULTS_PATH/combined.json"
}

# shellcheck disable=SC2207
repos=($(ls "$REPOS_PATH")) 
for r in "${repos[@]}"; do
    if [ "$DO_REDACTED" == "true" ]; then
        RESULTS_PATH="$ROOT_PATH/results/redacted"
        do_gitleaks "$r" "--redact"
    fi

    if [ "$DO_UNREDACTED" == "true" ]; then
        RESULTS_PATH="$ROOT_PATH/results/unredacted"
        do_gitleaks "$r" ""
    fi
done
