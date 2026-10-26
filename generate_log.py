import argparse
import random
from datetime import datetime, timedelta, timezone

PATHS = [
    ("/",                      30),
    ("/api/orders",            25),
    ("/api/orders/{id}",       15),
    ("/api/products",          12),
    ("/api/products/{id}",      8),
    ("/api/users/login",        5),
    ("/static/app.js",          3),
    ("/static/style.css",       2),
]
METHODS = [("GET", 85), ("POST", 10), ("PUT", 3), ("DELETE", 2)]
STATUS = [(200, 85), (201, 4), (301, 2), (400, 3), (404, 4), (500, 2)]

def weighted_choice(rng, items):
    values, weights = zip(*items)
    return rng.choices(values, weights=weights, k=1)[0]

def random_ip(rng):
    if rng.random() < 0.4:
        return f"10.0.0.{rng.randint(1, 20)}"
    return f"{rng.randint(1, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"

def random_size(rng):
    return max(0, int(rng.lognormvariate(mu=7.0, sigma=1.2)))

def generate(rows: int, out_path: str, seed: int = 42):
    rng = random.Random(seed)
    start = datetime(2025, 3, 14, 0, 0, 0, tzinfo=timezone.utc)
    step = timedelta(seconds=86400 / max(1, rows))
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for i in range(rows):
            ts = (start + step * i).strftime("%Y-%m-%dT%H:%M:%SZ")
            ip = random_ip(rng)
            method = weighted_choice(rng, METHODS)
            path = weighted_choice(rng, PATHS).replace("{id}", str(rng.randint(1, 9999)))
            status = weighted_choice(rng, STATUS)
            size = random_size(rng)
            f.write(f"{ts} {ip} {method} {path} {status} {size}\n")
    print(f"OK: {rows} строк записано в {out_path} (seed={seed})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=1000)
    ap.add_argument("--out", default="access.log")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    generate(args.rows, args.out, args.seed)
