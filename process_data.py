from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / 'data' / 'airbnb_listings.csv'
OUTPUT_JSON = ROOT / 'data' / 'airbnb_data.json'
PRICE_BUCKETS = [
    ('$0-50', 0, 50),
    ('$51-100', 51, 100),
    ('$101-150', 101, 150),
    ('$151-200', 151, 200),
    ('$201-300', 201, 300),
    ('$301+', 301, None),
]


def normalize_text(value: str | None, default: str = 'Unknown') -> str:
    if value is None:
        return default
    cleaned = value.strip()
    return cleaned if cleaned else default


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {'nan', 'null', 'none', 'n/a'}:
        return None
    filtered = ''.join(ch for ch in text if ch.isdigit() or ch in {'.', '-', '+'})
    if filtered in {'', '-', '+', '.', '-.', '+.'}:
        return None
    try:
        return float(filtered)
    except ValueError:
        return None


def init_scope() -> dict[str, Any]:
    return {
        'listings': 0,
        'price_total': 0.0,
        'price_count': 0,
        'reviews_total': 0.0,
        'review_count': 0,
        'availability_total': 0.0,
        'availability_count': 0,
        'hosts': set(),
        'room_type': defaultdict(lambda: {'count': 0, 'price_total': 0.0, 'price_count': 0}),
        'neighbourhoods': defaultdict(lambda: {'listings': 0, 'price_total': 0.0, 'price_count': 0}),
        'price_distribution': {label: 0 for label, _, _ in PRICE_BUCKETS},
    }


def bucket_for_price(price: float) -> str:
    for label, minimum, maximum in PRICE_BUCKETS:
        if maximum is None and price >= minimum:
            return label
        if minimum <= price <= maximum:
            return label
    return PRICE_BUCKETS[-1][0]


def update_scope(scope: dict[str, Any], row: dict[str, str]) -> None:
    price = parse_float(row.get('price'))
    if price is None or price < 0 or price > 1000:
        return

    scope['listings'] += 1
    scope['price_total'] += price
    scope['price_count'] += 1

    reviews = parse_float(row.get('number_of_reviews'))
    if reviews is not None:
        scope['reviews_total'] += reviews
        scope['review_count'] += 1

    availability = parse_float(row.get('availability_365'))
    if availability is not None:
        scope['availability_total'] += availability
        scope['availability_count'] += 1

    host_key = normalize_text(row.get('host_id') or row.get('host_name') or '')
    if host_key != 'Unknown':
        scope['hosts'].add(host_key)

    room_type = normalize_text(row.get('room_type'))
    room_stats = scope['room_type'][room_type]
    room_stats['count'] += 1
    room_stats['price_total'] += price
    room_stats['price_count'] += 1

    neighbourhood = normalize_text(row.get('neighbourhood'))
    neighbourhood_stats = scope['neighbourhoods'][neighbourhood]
    neighbourhood_stats['listings'] += 1
    neighbourhood_stats['price_total'] += price
    neighbourhood_stats['price_count'] += 1

    scope['price_distribution'][bucket_for_price(price)] += 1


def round_value(value: float | None, digits: int = 1) -> float:
    if value is None:
        return 0.0
    return round(value, digits)


def scope_to_payload(name: str | None, scope: dict[str, Any]) -> dict[str, Any]:
    kpis = {
        'total_listings': scope['listings'],
        'avg_price': round_value(scope['price_total'] / scope['price_count'] if scope['price_count'] else 0.0),
        'total_hosts': len(scope['hosts']),
        'avg_reviews': round_value(scope['reviews_total'] / scope['review_count'] if scope['review_count'] else 0.0),
    }

    room_type = [
        {
            'type': room_name,
            'count': values['count'],
            'avg_price': round_value(values['price_total'] / values['price_count'] if values['price_count'] else 0.0),
        }
        for room_name, values in sorted(scope['room_type'].items(), key=lambda item: (-item[1]['count'], item[0]))
    ]

    neighbourhoods = [
        {
            'name': neighbourhood_name,
            'listings': values['listings'],
            'avg_price': round_value(values['price_total'] / values['price_count'] if values['price_count'] else 0.0),
        }
        for neighbourhood_name, values in sorted(
            scope['neighbourhoods'].items(), key=lambda item: (-item[1]['listings'], item[0])
        )[:10]
    ]

    price_distribution = [
        {'range': label, 'count': scope['price_distribution'][label]}
        for label, _, _ in PRICE_BUCKETS
    ]

    payload = {
        'kpis': kpis,
        'by_room_type': room_type,
        'top_neighbourhoods': neighbourhoods,
        'price_distribution': price_distribution,
        'avg_availability': round(scope['availability_total'] / scope['availability_count']) if scope['availability_count'] else 0,
    }
    if name is not None:
        payload['borough'] = name
    return payload


with INPUT_CSV.open(newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    global_scope = init_scope()
    borough_scopes: dict[str, dict[str, Any]] = defaultdict(init_scope)

    for row in reader:
        borough = normalize_text(row.get('neighbourhood_group'))
        update_scope(global_scope, row)
        update_scope(borough_scopes[borough], row)

borough_payloads = {
    borough: scope_to_payload(borough, scope)
    for borough, scope in sorted(borough_scopes.items(), key=lambda item: (-item[1]['listings'], item[0]))
}

result = {
    'meta': {
        'source': 'Inside Airbnb',
        'city': 'New York City',
        'snapshot': '2024',
        'notes': 'Prices above $1000 are excluded as outliers. All values are pre-aggregated.',
    },
    'kpis': scope_to_payload(None, global_scope)['kpis'],
    'by_neighbourhood_group': [
        {
            'name': borough,
            'listings': payload['kpis']['total_listings'],
            'avg_price': payload['kpis']['avg_price'],
        }
        for borough, payload in borough_payloads.items()
    ],
    'by_room_type': scope_to_payload(None, global_scope)['by_room_type'],
    'top_neighbourhoods': [
        {
            'name': neighbourhood_name,
            'borough': borough,
            'listings': values['listings'],
            'avg_price': round_value(values['price_total'] / values['price_count'] if values['price_count'] else 0.0),
        }
        for borough, scope in borough_scopes.items()
        for neighbourhood_name, values in scope['neighbourhoods'].items()
    ],
    'price_distribution': scope_to_payload(None, global_scope)['price_distribution'],
    'availability_by_borough': [
        {
            'borough': borough,
            'avg_availability': payload['avg_availability'],
        }
        for borough, payload in borough_payloads.items()
    ],
    'borough_breakdowns': borough_payloads,
}

result['top_neighbourhoods'] = sorted(
    result['top_neighbourhoods'], key=lambda item: (-item['listings'], item['name'])
)[:10]

OUTPUT_JSON.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(f'Wrote {OUTPUT_JSON}')
