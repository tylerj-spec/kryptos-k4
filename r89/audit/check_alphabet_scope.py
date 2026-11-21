#!/usr/bin/env python3
"""Compare the original dev kit and R89 alphabet classes; no ciphertext is read.

Usage: check_alphabet_scope.py REPOSITORY ORIGINAL_KIT.zip OUT.json
The original reference file is hash checked and parsed, never executed.
"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

root, archive, output = map(Path, sys.argv[1:4])
with zipfile.ZipFile(archive) as z:
    names = [n for n in z.namelist() if n == 'reference.py' or n.endswith('/reference.py')]
    assert len(names) == 1
    body = z.read(names[0])
digest = hashlib.sha256(body).hexdigest()
assert digest == 'b263e44f8e34e66112965ad29f44bd255a1a3c5624469809fc292e3a393c36f7'
keywords = None
for node in ast.parse(body).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'KEYWORDS' for t in node.targets):
        keywords = ast.literal_eval(node.value)
assert keywords is not None
az = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
old = {word or 'AZ': ''.join(dict.fromkeys(word + az)) for word in keywords}
spec = importlib.util.spec_from_file_location('scope_only_f26', root / 'r89/f26l.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
new = module.F26_ALPHABETS

def canonical(alphabet):
    rows = tuple(sorted((''.join(sorted(alphabet[:13])), ''.join(sorted(alphabet[13:])))))
    columns = tuple(sorted(''.join(sorted((alphabet[k], alphabet[k + 13]))) for k in range(13)))
    return rows, columns

matches = {name: [n for n, a in new.items() if canonical(a) == canonical(alphabet)] for name, alphabet in old.items()}
result = {'old_reference_sha256': digest, 'old_alphabets': len(old),
          'old_distinct_canonical_classes': len({canonical(a) for a in old.values()}),
          'new_alphabets': len(new), 'new_distinct_canonical_classes': len({canonical(a) for a in new.values()}),
          'class_matches': matches, 'old_classes_covered': sum(bool(v) for v in matches.values()),
          'old_classes_not_covered': [k for k, v in matches.items() if not v]}
output.write_text(json.dumps(result, indent=2) + '\n')
print('Original classes explicitly covered:', result['old_classes_covered'], 'of', len(old))
