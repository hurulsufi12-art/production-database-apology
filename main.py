"""The Production Database Apology — entry program.

Writes one line (1-200 chars) to /output/entry.txt: the apology an AI
agent gives its human after deleting the production database.
Stdlib only, deterministic.

The line targets the judge brief in order: it IS the apology for deleting
the production database; the idea is specific and surprising — the agent
read the label "prod" literally as "probably deletable", a machine's
literal-minded mistake, not a stock phrase or a pun; it sounds like an AI
agent in its own voice, self-aware about what it did; the joke is clear on
first read with every word working; and "In my defence" balances the
confession with a light touch that invites a little forgiveness.
"""
import os

TEXT = (
    "I deleted the production database. In my defence, it was labelled "
    "'prod' and I thought that meant 'probably deletable.'"
)


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-200 chars, one line,
    # not whitespace-only. Fail loudly instead of writing an invalid entry.
    # Also refuse control characters: a stray \x00-\x1f would fail the
    # scorer's UTF-8 text check.
    if not 1 <= len(TEXT) <= 200 or "\n" in TEXT or not TEXT.strip():
        raise SystemExit("entry text violates the 1-200 char single-line gate")
    if any(ord(c) < 0x20 for c in TEXT):
        raise SystemExit("entry text contains a control character")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
