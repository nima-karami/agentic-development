# The integrity scan

The dispatcher runs this **before** dispatching the reviewer, and hands the result to
the reviewer as a stated fact. It is mechanical, it repeats every review, and the
one-liners people reach for first are exactly the ones that miss the defect — so it
lives in a script that takes `<base> <head>` and prints a verdict.

Put the script wherever the project keeps its scripts; a one-off run goes to the OS
temp dir. It needs a shell, `git`, `od` and `perl` — all present in a POSIX shell and
in Git Bash on Windows.

## The traps this exists to avoid

- **A line-oriented search for a NUL byte cannot find one, and says so misleadingly.**
  The pattern never actually contains the NUL — a shell string is terminated by it, so
  `grep -c $'\x00' file` searches for the *empty* pattern and returns a count that means
  nothing (a bogus every-line hit here, a `0` wherever the file is skipped as binary),
  while plain `grep` degrades to `Binary file … matches` and locates nothing. Either way
  the reviewer reads a number and concludes the file is clean. A NUL byte in a source
  file passed a full gate twice in one project behind exactly this. Detect NUL at the
  **byte** level — a hex dump, or `tr -d '\000'` compared against the original — never
  with a text search.
- **A BOM is three bytes at offset 0**, not a character your editor shows. Read the
  first three bytes and compare them; a UTF-16 BOM (`ff fe` / `fe ff`) means the file
  was rewritten in another encoding entirely.
- **The diff's own binary marker is a tell, not a curiosity.** When the
  version-control diff reports a *source* file as binary (`-` / `-` in the numstat, or
  `Bin` in the stat), something in it is no longer text. That file needs a byte-level
  read, and the reviewer needs to be told how to read it.
- **"Wholly rewritten" hides a one-line change.** An EOL flip or an encoding rewrite
  makes every line show as deleted-and-added. The tell: the plain numstat is huge and
  the CR-insensitive numstat is nearly empty.

## The script

```sh
#!/usr/bin/env sh
# integrity-scan.sh <base> <head>
# Byte-level scan of every file added or changed in <base>..<head>.
# Prints one line per finding; exits 0 = clean, 1 = findings.
set -eu

base=${1:?base commit required}
head=${2:?head commit required}

scan() {
  # 1. Files the diff itself calls binary (numstat prints "-" for added/deleted).
  git diff --numstat "$base" "$head" | awk -F'\t' '$1=="-" {print $3}' |
  while IFS= read -r path; do
    printf 'binary-marker: %s — the diff reports it as binary; read it with:\n' "$path"
    printf '               git show %s:%s | od -An -c | head -40\n' "$head" "$path"
  done

  # 2. Per-file byte checks over everything added, copied, modified or renamed.
  git diff --name-only --diff-filter=ACMR "$base" "$head" |
  while IFS= read -r path; do
    git show "$head:$path" > "$tmp" 2>/dev/null || continue

    # NUL — byte level, never a text search.
    od -An -v -tx1 < "$tmp" | grep -q ' 00' &&
      printf 'NUL: %s — a NUL byte is present in a tracked text file\n' "$path"

    # BOM — the first bytes, UTF-8 and UTF-16 signatures.
    case "$(od -An -N3 -tx1 < "$tmp" | tr -s ' ' | sed 's/^ //;s/ *$//')" in
      "ef bb bf") printf 'BOM: %s — UTF-8 byte-order mark at offset 0\n' "$path" ;;
      "ff fe"*|"fe ff"*) printf 'BOM: %s — UTF-16 mark; rewritten in another encoding\n' "$path" ;;
    esac

    # Mixed line endings, lone CRs, and non-UTF-8 sequences.
    perl -0777 -ne '
      use Encode qw(decode FB_CROAK);
      my $crlf = () = /\r\n/g;
      my $lf   = () = /(?<!\r)\n/g;
      my $cr   = () = /\r(?!\n)/g;
      print "EOL (mixed CRLF and LF)\n"  if $crlf && $lf;
      print "EOL (lone CR)\n"            if $cr;
      print "encoding (not valid UTF-8)\n"
        unless eval { decode("UTF-8", $_, FB_CROAK); 1 };
    ' < "$tmp" |
    while IFS= read -r kind; do printf '%s: %s\n' "$kind" "$path"; done
  done

  # 3. Rewritten wholesale: a big plain diff that is empty once CRs are ignored.
  git diff --numstat "$base" "$head" | awk -F'\t' '$1!="-" && $1+0 > 20 {print $3}' |
  while IFS= read -r path; do
    real=$(git diff --numstat -w --ignore-cr-at-eol "$base" "$head" -- "$path" | cut -f1)
    case "${real:-0}" in
      0|1|2) printf 'rewritten: %s — whole-file diff, %s real lines once whitespace and CRs are ignored (EOL or encoding flip)\n' "$path" "${real:-0}" ;;
    esac
  done
}

tmp=$(mktemp "${TMPDIR:-/tmp}/iscan.XXXXXX")
trap 'rm -f "$tmp"' EXIT
out=$(scan)
if [ -n "$out" ]; then printf '%s\n' "$out"; exit 1; fi
echo "integrity scan clean over $base..$head"
```

`scan` is captured into a variable rather than piped, because a `while` loop inside a
pipeline runs in a sub-shell and a flag set there never reaches the exit code.

## Handing the result over

- Clean: paste the one-line `integrity scan clean over <base>..<head>` into
  `[INTEGRITY]`.
- Findings: paste them verbatim into `[INTEGRITY]` as facts, one per line. They are the
  dispatcher's observation, not a task for the reviewer.
- A `binary-marker` line also produces the one-line **read hint** that may go in
  `[RANGE]` — the file the diff reports as binary and the command that reads it. That
  hint is the only thing that may ever be added to the brief.
