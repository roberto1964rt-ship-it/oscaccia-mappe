#!/usr/bin/env python3
"""Build a raster PNG MBTiles package from a locally rendered OSM tile server."""

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import sqlite3
import struct
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BOUNDS = (12.70, 41.55, 14.90, 43.10)  # Abruzzo plus a small edge margin
ATTRIBUTION = "© OpenStreetMap contributors"
MAX_RELEASE_ASSET = 1_900_000_000  # keep below GitHub's 2 GiB per-asset limit


def lon_to_x(lon: float, zoom: int) -> int:
    return int(math.floor((lon + 180.0) / 360.0 * (1 << zoom)))


def lat_to_y(lat: float, zoom: int) -> int:
    lat_rad = math.radians(lat)
    value = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * (1 << zoom)
    return int(math.floor(value))


def fetch_tile(args):
    base_url, z, x, y = args
    url = f"{base_url.rstrip('/')}/{z}/{x}/{y}.png"
    last_error = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "OSCACCIA-offline-map-builder/1.0"}
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                data = response.read()
            if not data.startswith(b"\x89PNG\r\n\x1a\n"):
                raise RuntimeError(f"Tile is not PNG: {url}")
            if len(data) < 24 or struct.unpack(">II", data[16:24]) != (256, 256):
                raise RuntimeError(f"Tile dimensions are not 256x256: {url}")
            return z, x, y, data
        except Exception as exc:
            last_error = exc
            time.sleep(min(2 ** attempt, 12))
    raise RuntimeError(f"Unable to fetch {url}: {last_error}")


def make_db(path: Path):
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("PRAGMA temp_store=MEMORY")
    db.execute("""
        CREATE TABLE metadata (name TEXT PRIMARY KEY, value TEXT)
    """)
    db.execute("""
        CREATE TABLE tiles (
            zoom_level INTEGER NOT NULL,
            tile_column INTEGER NOT NULL,
            tile_row INTEGER NOT NULL,
            tile_data BLOB NOT NULL,
            PRIMARY KEY (zoom_level, tile_column, tile_row)
        ) WITHOUT ROWID
    """)
    return db


def set_metadata(db, min_zoom, max_zoom, tile_count):
    west, south, east, north = BOUNDS
    center_lon = (west + east) / 2.0
    center_lat = (south + north) / 2.0
    values = {
        "name": "OSCACCIA Abruzzo",
        "type": "baselayer",
        "version": "1.3",
        "description": "Mappa offline raster PNG del Abruzzo e delle aree di margine. Dati OpenStreetMap.",
        "format": "png",
        "bounds": f"{west},{south},{east},{north}",
        "center": f"{center_lon},{center_lat},9",
        "minzoom": str(min_zoom),
        "maxzoom": str(max_zoom),
        "attribution": ATTRIBUTION,
        "tile_count": str(tile_count),
    }
    db.executemany(
        "INSERT OR REPLACE INTO metadata(name, value) VALUES(?, ?)",
        list(values.items())
    )


def generate(base_url: str, output: Path, min_zoom: int, max_zoom: int, workers: int):
    db = make_db(output)
    tile_count = 0
    tile_batch = []
    batch_size = 600
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for z in range(min_zoom, max_zoom + 1):
                n = 1 << z
                x_min = max(0, lon_to_x(BOUNDS[0], z))
                x_max = min(n - 1, lon_to_x(BOUNDS[2], z))
                y_min = max(0, lat_to_y(BOUNDS[3], z))
                y_max = min(n - 1, lat_to_y(BOUNDS[1], z))
                coords = [
                    (base_url, z, x, y)
                    for x in range(x_min, x_max + 1)
                    for y in range(y_min, y_max + 1)
                ]
                print(
                    f"Zoom {z}: {len(coords)} tiles "
                    f"(x {x_min}-{x_max}, y {y_min}-{y_max})",
                    flush=True
                )
                for start in range(0, len(coords), batch_size):
                    batch = coords[start:start + batch_size]
                    for result in pool.map(fetch_tile, batch):
                        rz, x, y, data = result
                        tms_y = (1 << rz) - 1 - y
                        tile_batch.append((rz, x, tms_y, sqlite3.Binary(data)))
                        tile_count += 1
                    if len(tile_batch) >= batch_size:
                        db.executemany(
                            "INSERT INTO tiles(zoom_level, tile_column, tile_row, tile_data) VALUES(?, ?, ?, ?)",
                            tile_batch
                        )
                        db.commit()
                        tile_batch.clear()
                    if tile_count % 3000 < batch_size:
                        print(f"Tiles salvate: {tile_count}", flush=True)

        if tile_batch:
            db.executemany(
                "INSERT INTO tiles(zoom_level, tile_column, tile_row, tile_data) VALUES(?, ?, ?, ?)",
                tile_batch
            )
            db.commit()
            tile_batch.clear()

        set_metadata(db, min_zoom, max_zoom, tile_count)
        db.commit()
        db.close()

        size = output.stat().st_size
        if size > MAX_RELEASE_ASSET and max_zoom > min_zoom:
            print(
                f"MBTiles {size} bytes: oltre il margine prudenziale per GitHub. "
                f"Rimuovo lo zoom massimo {max_zoom}.",
                flush=True
            )
            db = sqlite3.connect(output)
            db.execute("DELETE FROM tiles WHERE zoom_level = ?", (max_zoom,))
            db.execute("UPDATE metadata SET value = ? WHERE name = 'maxzoom'", (str(max_zoom - 1),))
            db.execute(
                "UPDATE metadata SET value = (SELECT COUNT(*) FROM tiles) WHERE name = 'tile_count'"
            )
            db.commit()
            db.execute("VACUUM")
            db.close()
            max_zoom -= 1

        size = output.stat().st_size
        if size > MAX_RELEASE_ASSET:
            raise RuntimeError(
                f"MBTiles troppo grande ({size} byte). Ridurre il livello massimo di zoom."
            )

        db = sqlite3.connect(output)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        fmt = db.execute("SELECT value FROM metadata WHERE name='format'").fetchone()[0]
        count = db.execute("SELECT COUNT(*) FROM tiles").fetchone()[0]
        sample = db.execute(
            "SELECT tile_data FROM tiles ORDER BY zoom_level DESC LIMIT 1"
        ).fetchone()
        db.close()
        if integrity != "ok" or fmt != "png" or count == 0:
            raise RuntimeError(f"Verifica MBTiles fallita: integrity={integrity}, format={fmt}, tiles={count}")
        if not sample or not bytes(sample[0]).startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("Il tile di controllo non è una PNG valida")

        digest = hashlib.sha256()
        with output.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)

        manifest = {
            "id": "it-abruzzo",
            "name": "Abruzzo",
            "country": "Italia",
            "version": "1.0.0",
            "format": "mbtiles",
            "tile_format": "png",
            "min_zoom": min_zoom,
            "max_zoom": max_zoom,
            "bounds": list(BOUNDS),
            "size_bytes": size,
            "sha256": digest.hexdigest(),
            "tile_count": count,
            "attribution": ATTRIBUTION,
            "license": "ODbL",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "validation": "sqlite_integrity_ok_png_tiles_ok",
        }
        output.with_suffix(".json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
        return manifest
    except Exception:
        try:
            db.close()
        except Exception:
            pass
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/tile")
    parser.add_argument("--output", default="dist/oscaccia-abruzzo-v1.0.0.mbtiles")
    parser.add_argument("--min-zoom", type=int, default=7)
    parser.add_argument("--max-zoom", type=int, default=15)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.min_zoom < 0 or args.max_zoom > 18 or args.min_zoom > args.max_zoom:
        parser.error("Intervallo zoom non valido (0 <= min <= max <= 18)")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    generate(args.base_url, output, args.min_zoom, args.max_zoom, args.workers)


if __name__ == "__main__":
    main()
