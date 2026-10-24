import urllib.request
import json

endpoints = [
    ('Frontend Vite Dev Server', 'http://127.0.0.1:5173/'),
    ('API Health', 'http://127.0.0.1:8000/api/health'),
    ('API Summary (Jan 2026)', 'http://127.0.0.1:8000/api/summary?cutoff=12:00&startDate=2026-01-01&endDate=2026-01-31'),
    ('API Metrics Breakdown', 'http://127.0.0.1:8000/api/metrics?cutoff=12:00&startDate=2026-01-01&endDate=2026-01-31'),
    ('API Timeseries (2026-01-15)', 'http://127.0.0.1:8000/api/timeseries?date=2026-01-15&cutoff=12:00'),
    ('API Forecast Evolution', 'http://127.0.0.1:8000/api/forecast-evolution?date=2026-01-15')
]

print("=== LIVE INTEGRATION VERIFICATION ===")
for name, url in endpoints:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            status = r.status
            content = r.read().decode('utf-8')
            if 'api' in url:
                data = json.loads(content)
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"[SUCCESS] {name} -> HTTP {status} OK | Response keys: {keys[:5]}")
                    if 'maeMW' in data:
                        print(f"          MAE: {data['maeMW']} MW, WAPE: {data['wapePct']}%, Matched: {data['matchedHours']}/{data['totalHours']}")
                else:
                    print(f"[SUCCESS] {name} -> HTTP {status} OK")
            else:
                has_root = 'id="root"' in content
                title = content.split('<title>')[1].split('</title>')[0] if '<title>' in content else 'N/A'
                print(f"[SUCCESS] {name} -> HTTP {status} OK | Title: '{title}' | Root div present: {has_root}")
    except Exception as e:
        print(f"[FAILED]  {name} -> {e}")
