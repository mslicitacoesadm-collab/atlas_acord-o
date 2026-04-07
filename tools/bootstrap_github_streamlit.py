from __future__ import annotations

from pathlib import Path

from tools.rebuild_base_from_parts import rebuild
from tools.verify_base import verify

PARTS_DIR = Path('base_inteligente_atlas')
OUTPUT_DB = Path('data/base/base_inteligente.db')


def main() -> None:
    if OUTPUT_DB.exists():
        print(f'Base já existe em {OUTPUT_DB}')
        print('Integridade:', verify(OUTPUT_DB))
        return
    rebuilt = rebuild(PARTS_DIR, OUTPUT_DB)
    print(f'Base reconstruída: {rebuilt}')
    print('Integridade:', verify(rebuilt))


if __name__ == '__main__':
    main()
