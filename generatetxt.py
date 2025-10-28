import os
import csv

# ---------------- Settings ----------------
TEST_FOLDER = "texts_to_analyze"

# ---------------- Create test folder ----------------
os.makedirs(TEST_FOLDER, exist_ok=True)

# ---------------- Sample text files ----------------
sample_texts = {
    "file1.txt": "I feel happy today! Life is beautiful and exciting.",
    "file2.txt": "I am sad and anxious about work. Nothing seems to go right.",
    "file3.txt": "Feeling stressed, tired, and overwhelmed. Need a vacation soon."
}

for fname, text in sample_texts.items():
    with open(os.path.join(TEST_FOLDER, fname), "w", encoding="utf-8") as f:
        f.write(text)

print(f"Created {len(sample_texts)} test text files in '{TEST_FOLDER}'")


stopwords_list = """a
an
the
and
or
but
in
on
at
to
for
of
with
by
from
as
is
was
are
be
been
being
have
has
had
do
does
did
will
would
should
could
may
might
can
i
you
he
she
it
we
they
me
him
her
us
them
my
your
his
its
our
their
this
that
these
those"""

stopwords_path = "/scratch/network/sm9518/python_test/vocabulate/stopwords.txt"

with open(stopwords_path, "w", encoding="utf-8") as f:
    f.write(stopwords_list)

print(f"Stopwords saved to {stopwords_path}")
