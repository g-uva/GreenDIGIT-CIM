import json, random
from datetime import datetime, timezone, timedelta

N = 100_000 # Number of lines
base = datetime(2025, 9, 1, 12, 0, 0, tzinfo=timezone.utc)

with open("input.json", "w", encoding="utf-8") as f:
    f.write('[')
    for i in range(N):
        obj = {
            "metric": "cpu.util" if i % 3 else "mem.used",
            "value": round(random.random() * 100, 3),
            "ts": (base + timedelta(seconds=i)).isoformat(),
            "node": f"compute-{i % 5}",
            "i": i
        }
        json.dump(obj, f, separators=(',', ':'), ensure_ascii=False)
        if i != N - 1:
            f.write(',')
    f.write(']')
