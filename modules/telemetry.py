from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

TELEMETRY_DIR = Path(__file__).resolve().parent.parent / 'exports' / 'telemetry'
EVENTS_FILE = TELEMETRY_DIR / 'events.jsonl'
SUMMARY_FILE = TELEMETRY_DIR / 'summary.json'


def _ensure_dir() -> None:
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    _ensure_dir()
    event = {
        'ts': datetime.utcnow().isoformat() + 'Z',
        'event_type': event_type,
        'payload': payload,
    }
    with EVENTS_FILE.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + '\n')
    rebuild_summary()


def _read_events() -> List[Dict[str, Any]]:
    if not EVENTS_FILE.exists():
        return []
    events: List[Dict[str, Any]] = []
    for line in EVENTS_FILE.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events


def rebuild_summary() -> Dict[str, Any]:
    events = _read_events()
    by_type = Counter(evt.get('event_type') for evt in events)
    top_theses = Counter()
    top_status = Counter()
    top_piece_types = Counter()
    total_citations = 0
    total_errors = 0
    total_adjustments = 0

    for evt in events:
        payload = evt.get('payload') or {}
        thesis = payload.get('thesis')
        if thesis:
            top_theses[thesis] += 1
        piece_type = payload.get('piece_type')
        if piece_type:
            top_piece_types[piece_type] += 1
        status = payload.get('status')
        if status:
            top_status[status] += 1
        total_citations += int(payload.get('citations', 0) or 0)
        total_errors += int(payload.get('errors', 0) or 0)
        total_adjustments += int(payload.get('adjustments', 0) or 0)

    summary = {
        'total_eventos': len(events),
        'por_tipo_evento': dict(by_type),
        'teses_mais_frequentes': top_theses.most_common(10),
        'tipos_peca_mais_frequentes': top_piece_types.most_common(10),
        'status_mais_frequentes': top_status.most_common(10),
        'citacoes_processadas': total_citations,
        'erros_relevantes': total_errors,
        'ajustes_recomendados': total_adjustments,
    }
    _ensure_dir()
    SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary


def get_summary() -> Dict[str, Any]:
    if SUMMARY_FILE.exists():
        try:
            return json.loads(SUMMARY_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return rebuild_summary()
