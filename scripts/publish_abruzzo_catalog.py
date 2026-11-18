#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path

catalog_path = Path("catalog/catalog.json")
manifest_path = Path("dist/oscaccia-abruzzo-v1.0.0.json")
repo = os.environ["GITHUB_REPOSITORY"]
tag = os.environ.get("RELEASE_TAG", "it-abruzzo-v1.0.0")
asset_name = "oscaccia-abruzzo-v1.0.0.mbtiles"

catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
maps = catalog.setdefault("maps", [])
matches = [item for item in maps if item.get("id") == "it-abruzzo"]
if len(matches) > 1:
    raise SystemExit("Catalogo: trovate più voci con id it-abruzzo")
item = matches[0] if matches else {}
if not matches:
    maps.append(item)

item.update({
    "id": "it-abruzzo",
    "name": "Abruzzo",
    "country": "Italia",
    "country_code": "IT",
    "region": "Abruzzo",
    "version": manifest["version"],
    "status": "available",
    "format": "mbtiles",
    "tile_format": "png",
    "min_zoom": manifest["min_zoom"],
    "max_zoom": manifest["max_zoom"],
    "size_bytes": manifest["size_bytes"],
    "sha256": manifest["sha256"],
    "download_url": f"https://github.com/{repo}/releases/download/{tag}/{asset_name}",
    "attribution": "© OpenStreetMap contributors",
    "license": "ODbL",
    "bounds": manifest["bounds"],
    "notes": "Pacchetto raster MBTiles PNG verificato automaticamente prima della pubblicazione."
})
catalog["generated_at"] = datetime.now(timezone.utc).isoformat()
catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Catalogo aggiornato: {item['download_url']}")
