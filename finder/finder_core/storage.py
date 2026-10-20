"""Local JSON store. Lock read-modify-write operations and replace files atomically."""
import json
import os
from pathlib import Path
import tempfile
from filelock import FileLock
from .vocabulary import VOCAB

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'data/items.seed.json'
FIELDS = {'category', 'color', 'brand', 'location', 'mark'}


def data_path():
    return Path(os.environ.get('FINDER_DATA_PATH') or ROOT / 'runtime/items.json').resolve()


def validate_fields(values):
    if set(values) != FIELDS:
        raise ValueError('Expected category, color, brand, location and mark fields.')
    vocab_map = {
        'category': 'categories',
        'color': 'colors',
        'brand': 'brands',
        'location': 'locations',
        'mark': 'marks'
    }
    result = {}
    for field in sorted(FIELDS):
        value = values[field]
        if value is None and field in {'brand', 'mark'}:
            result[field] = None
            continue
        if not isinstance(value, str):
            raise ValueError(f'Invalid {field}.')
        value = value.strip().lower()
        if value not in VOCAB[field]:
            raise ValueError(f'Choose a supported {field}.')
        result[field] = value
    return result


def validate_items(items):
    if not isinstance(items, list):
        raise ValueError('Item file must contain a JSON list.')
    seen = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != FIELDS | {'id', 'status'}:
            raise ValueError('Invalid item record fields.')
        if type(item['id']) is not int or item['id'] < 1 or item['id'] in seen:
            raise ValueError('Item IDs must be unique positive integers.')
        seen.add(item['id'])
        if not isinstance(item['status'], str) or item['status'] not in {'available', 'returned'}:
            raise ValueError('Invalid item status.')
        if validate_fields({k:item[k] for k in FIELDS}) != {k:item[k] for k in FIELDS}:
            raise ValueError('Stored values must be canonical.')
    return items


def _read(path):
    return validate_items(json.loads(path.read_text(encoding='utf-8-sig')))


def _write(path, items):
    validate_items(items)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.items-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(items, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _load(path):
    if not path.exists():
        _write(path, _read(SEED))
    return _read(path)


def load_items(path=None):
    path = Path(path) if path is not None else data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path)+'.lock', timeout=5):
        return _load(path)


def add_item(values, path=None):
    values = validate_fields(values)
    path = Path(path) if path is not None else data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path)+'.lock', timeout=5):
        items = _load(path)
        item = {'id':max((row['id'] for row in items), default=0)+1, **values, 'status':'available'}
        _write(path, items+[item])
        return item


def mark_returned(item_id, path=None):
    if type(item_id) is not int or item_id < 1:
        raise ValueError('Choose a valid item ID.')
    path = Path(path) if path is not None else data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path)+'.lock', timeout=5):
        items = _load(path)
        item = next((row for row in items if row['id']==item_id), None)
        if item is None:
            raise ValueError('Item was not found.')
        if item['status'] != 'available':
            raise ValueError('Item has already been returned. Refresh the page.')
        item['status'] = 'returned'
        _write(path, items)
        return item
