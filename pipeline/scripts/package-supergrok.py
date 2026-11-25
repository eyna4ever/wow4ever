"""Prepare an isolated third-party audit ZIP; never copy active hosting identity or secrets."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PARTS = {'.git', '.openai', '.aws', '.codex', '.agents', 'node_modules', '.next', '__pycache__', 'runtime', 'artifacts', 'dist', 'preview'}
SECRET_PATTERNS = {
    'private-key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'active-sites-id': rb'\bappg(?:prj|dep|ver|dom)_[A-Za-z0-9_~.-]{8,}',
    'dns-proof': rb'openai-site-verification=[A-Za-z0-9_-]{20,}',
    'github-token': rb'\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}',
    'api-key': rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}',
    'aws-access-key': rb'\bAKIA[A-Z0-9]{16}\b',
    'jwt': rb'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
}


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    artifacts = ROOT / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='supergrok-', dir=artifacts) as temporary:
        stage = Path(temporary)
        payload = set()
        transformations = []

        def put(name, body):
            path = stage / name
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            payload.add(name)

        def copy(path, name):
            if path.is_symlink() or not path.is_file():
                raise ValueError('Missing or symbolic source: ' + str(path.relative_to(ROOT)))
            put(name, path.read_bytes())

        fixed = ['README.md', 'package.json', 'tsconfig.json', 'next.config.ts', 'Dockerfile', '.gitignore', '.dockerignore', '.env.example']
        for filename in fixed:
            copy(ROOT / filename, 'source/' + filename)
        for filename in ['package-lock.json', 'pnpm-lock.yaml', 'yarn.lock']:
            if (ROOT / filename).is_file():
                copy(ROOT / filename, 'source/' + filename)
        for directory in ['app', 'lib', 'scripts', 'tests', 'data', 'db', 'docs', 'design', 'public']:
            for path in sorted((ROOT / directory).rglob('*')):
                relative = path.relative_to(ROOT)
                if any(part in BLOCKED_PARTS for part in relative.parts) or path.is_symlink() or not path.is_file():
                    continue
                if path.name.startswith('.env') or path.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'}:
                    continue
                if relative.parts[:3] == ('public', 'wiki', 'assets') and path.suffix.lower() == '.png':
                    continue  # Lossless WebP assets are shipped; keep the two design reference PNGs.
                if relative.as_posix() == 'docs/CUSTOM-DOMAIN.md':
                    continue
                if path.suffix.lower() not in {'.md', '.json', '.mjs', '.cjs', '.js', '.ts', '.mts', '.cts', '.tsx', '.css', '.html', '.py', '.sql', '.webmanifest', '.svg', '.webp', '.png'}:
                    continue
                body = path.read_bytes()
                if relative.as_posix() == 'docs/RESEARCH.md':
                    text = body.decode('utf-8')
                    text = re.sub(r'^Le catalogue local .*?\n', 'La recherche historique n’a pas établi de dépôt d’origine ni d’affiliation du wiki à un autre projet.\n', text, flags=re.MULTILINE)
                    body = text.encode('utf-8')
                    transformations.append({'path': 'source/docs/RESEARCH.md', 'reason': 'Référence au registre privé d’un autre projet retirée.'})
                put('source/' + relative.as_posix(), body)
        for filename in ['compose.static.yaml', 'nginx.conf.example']:
            copy(ROOT / 'deploy' / filename, 'source/deploy/' + filename)
        put('source/docs/CUSTOM-DOMAIN.md', '# Hébergement — copie neutralisée pour audit\n\nLa démonstration possède déjà son hébergement et son domaine wow4ever.raveforge.eu. Leur état historique est décrit dans le prompt. Aucun accès, identifiant de projet ou preuve DNS n’est transmis. Ne créer aucun nouveau site et ne modifier aucun DNS ou déploiement pendant cet audit. Le propriétaire conserve la configuration active hors de cette archive.\n')
        transformations.append({'path': 'source/docs/CUSTOM-DOMAIN.md', 'reason': 'Copie neutralisée ; configuration de production et preuves DNS exclues.'})
        copy(ROOT / 'handoff-supergrok/PROMPT-SUPERGROK.md', 'PROMPT-SUPERGROK.md')
        copy(ROOT / 'artifacts/wow-forever-integre.html', 'apercu-site.html')
        for filename in ['LIRE-MOI.txt', 'entries.json', 'wiki.sqlite', 'relecture.html', 'content-report.json', 'content-report.md', 'forever-classes-sources.json', 'forever-world-sources.json', 'forever-systems-sources.json', 'manifest.json']:
            copy(ROOT / 'artifacts/content-package' / filename, 'documentation/' + filename)
        copy(ROOT / 'handoff-supergrok/tests-2026-10-24.log', 'verification/tests-espace-travail.log')

        checks = []
        source = stage / 'source'
        commands = [
            ['npm', 'test'],
            ['node', 'scripts/import-library.mjs', '--dry-run'],
            ['node', 'scripts/build-static.mjs'],
            ['node', 'scripts/check-release.mjs', 'artifacts/wow-forever-integre.html', 'data/entries.json'],
        ]
        for index, command in enumerate(commands, 1):
            log = stage / f'check-{index}.log'
            with log.open('wb') as handle:
                result = subprocess.run(command, cwd=source, stdin=subprocess.DEVNULL, stdout=handle, stderr=subprocess.STDOUT, timeout=60)
            name = f'verification/copie-isolee-{index}.log'
            put(name, log.read_bytes())
            checks.append({'command': command, 'exitCode': result.returncode, 'log': name})
            if result.returncode:
                raise RuntimeError('Audit copy check failed; consult ' + name)
        if (source / 'artifacts/wow-forever-integre.html').read_bytes() != (stage / 'apercu-site.html').read_bytes():
            raise RuntimeError('Standalone preview does not match the clean source rebuild')
        database = sqlite3.connect('file:' + str(stage / 'documentation/wiki.sqlite') + '?mode=ro', uri=True)
        try:
            integrity = database.execute('PRAGMA integrity_check').fetchone()[0]
            foreign_keys = database.execute('PRAGMA foreign_key_check').fetchall()
            rows = database.execute('SELECT status,count(*) FROM wiki_entries GROUP BY status').fetchall()
            categories = database.execute('SELECT count(DISTINCT category) FROM wiki_entries').fetchone()[0]
            if integrity != 'ok' or foreign_keys or rows != [('draft', 36)] or categories != 12:
                raise RuntimeError('Unexpected SQLite integrity or editorial state')
        finally:
            database.close()
        test_log = (stage / 'verification/copie-isolee-1.log').read_text()
        if not re.search(r'\bpass 112\b', test_log) or not re.search(r'\bfail 0\b', test_log):
            raise RuntimeError('Expected explicit 112-test result from isolated source')
        state = {
            'preparedOn': '2026-10-24', 'userTimezone': 'Europe/Paris',
            'records': 36, 'drafts': 36, 'published': 0, 'categories': 12, 'referenceURLs': 24, 'distinctArticles': 14,
            'documentarySourceAccessedOn': '2026-10-19', 'gameScopeConfirmedByOwner': False,
            'tests': {'executedOn': '2026-10-24', 'passed': 112, 'failed': 0, 'environment': 'isolated source copy without active hosting identity'},
            'checks': checks, 'sqlite': {'integrity': integrity, 'foreignKeyErrors': len(foreign_keys)},
            'browserAndroidQA': 'not executed for this package', 'nextBuild': 'not executed; dependencies not installed',
            'remoteSiteCheckedToday': False, 'remoteChangesPerformed': False,
            'hostedDatabase': 'not connected; included SQLite is a local export',
            'portabilityNotes': ['Node.js 24 and Python 3 required.', 'Some older packaging scripts hardcode /workspace/shared/downloads; use the individual relative-path commands in LIRE-MOI.', 'Active .openai hosting identity is intentionally absent.'],
            'sourceTransformations': transformations,
        }
        put('ETAT-VERIFIE.json', json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        put('LIRE-MOI-SUPERGROK.md', '''# Archive de travail pour SuperGrok

1. Joindre ce ZIP à SuperGrok et lui demander de lire `PROMPT-SUPERGROK.md`, puis d’analyser et corriger la copie isolée.
2. `source/` contient le code, les tests, les scripts, les lots documentaires et les références graphiques. Il n’y a ni historique Git ni identité de production active.
3. Ouvrir `apercu-site.html` pour voir l’interface réelle sans installation. Le catalogue public contient 0 fiche ; les 36 notices restent en brouillon.
4. Ouvrir `documentation/relecture.html` pour consulter les 36 notices FR/EN. Ce dossier privé inclut JSON, SQLite et rapport de couverture. Il ne doit pas être servi comme site public.
5. Lire `ETAT-VERIFIE.json` et `verification/` pour les contrôles réellement exécutés le 24 octobre 2026. 112 tests passent dans une copie isolée du code transmis. La reconstruction de l’aperçu est identique.

## Commandes locales depuis source/

Node.js 24 et Python 3 suffisent pour la partie statique et documentaire, sans installation de dépendances :

```sh
npm test
node scripts/import-library.mjs --dry-run
node scripts/import-library.mjs
node scripts/check-data.mjs runtime/entries.json
node scripts/content-review.mjs --output artifacts/relecture.html
node scripts/export-content-sqlite.mjs --output artifacts/wiki.sqlite
npm run build:static
```

Les anciens scripts `prepare-content.mjs`, `package-local.py` et `export-preview.py` utilisent un chemin de téléchargement propre à l’ancien environnement. Cela fait partie des points de portabilité à corriger ; les commandes individuelles ci-dessus utilisent des chemins relatifs. Les dépendances Next.js ne sont pas installées et leur compilation n’a pas été exécutée ici.

## Confidentialité, graphisme et limites

Les secrets, accès, identifiants de production, preuves DNS, historiques Git et anciens journaux de déploiement sont exclus. Le modèle `.env.example` contient uniquement une valeur localhost `CHANGE_ME`. Les documents neutralisés sont recensés dans le manifeste. Aucun accès au site distant ni autorisation de le modifier n’est donné par cette archive.

Les deux PNG de `source/design/` sont des références de conception ; ils ne prouvent pas le rendu du code. Les illustrations utilisées par le site sont fournies en WebP sans perte. Les PNG d’assets identiques décodés ne sont pas dupliqués. La provenance et les limites de droits sont décrites dans `source/docs/ASSETS.md`.

Les faits viennent d’annonces et de bêta consultées le 19 octobre. Ils doivent être réexaminés au 24 octobre, particulièrement l’état de la bêta annoncé jusqu’au 21 octobre. L’identité éditoriale du wiki reste à confirmer par son propriétaire. Aucune autre IA ne doit signer une validation humaine ou publier les brouillons pour remplir artificiellement le site.

Demander en retour : code corrigé, rapport P0/P1/P2, tests réellement exécutés et nouvelle archive ZIP. Ne pas demander une publication sur le site actif.
''')
        findings = []
        for name in sorted(payload):
            body = (stage / name).read_bytes()
            for label, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, body):
                    findings.append({'file': name, 'rule': label})
        if findings:
            raise RuntimeError('Archive rejected by identifier/secret scan: ' + json.dumps(findings))
        manifest = {
            'schema': 1, 'preparedOn': '2026-10-24',
            'scan': {'matchedSensitivePatterns': 0, 'patterns': list(SECRET_PATTERNS), 'scope': 'All packaged bytes; pattern checks are not a universal guarantee.'},
            'sourceTransformations': transformations,
            'files': [{'path': name, 'bytes': (stage / name).stat().st_size, 'sha256': sha((stage / name).read_bytes())} for name in sorted(payload)],
        }
        put('MANIFEST-SHA256.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        temporary_zip = output.with_suffix(output.suffix + '.tmp')
        try:
            with zipfile.ZipFile(temporary_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for name in sorted(payload):
                    info = zipfile.ZipInfo('wow-forever-supergrok/' + name)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, (stage / name).read_bytes())
            with zipfile.ZipFile(temporary_zip) as archive:
                if archive.testzip() is not None or len(set(archive.namelist())) != len(payload):
                    raise RuntimeError('ZIP integrity failure')
                for name in archive.namelist():
                    if '..' in PurePosixPath(name).parts or name.startswith('/'):
                        raise RuntimeError('Unsafe ZIP path')
                for item in manifest['files']:
                    if sha(archive.read('wow-forever-supergrok/' + item['path'])) != item['sha256']:
                        raise RuntimeError('ZIP checksum mismatch')
            temporary_zip.replace(output)
        finally:
            temporary_zip.unlink(missing_ok=True)
        checksum = sha(output.read_bytes())
        output.with_suffix(output.suffix + '.sha256').write_text(checksum + '  ' + output.name + '\n')
        print(json.dumps({'archive': str(output), 'bytes': output.stat().st_size, 'files': len(payload), 'sha256': checksum, 'testsPassed': 112, 'secretPatternMatches': 0}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
