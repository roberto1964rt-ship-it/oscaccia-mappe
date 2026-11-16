# Integrazione app OSCACCIA

Le pagine Capo e Cacciatore/Capocaccia usano lo stesso catalogo remoto:

`https://raw.githubusercontent.com/roberto1964rt-ship-it/oscaccia-mappe/main/catalog/catalog.json`

## Flusso nell'app

1. Il pulsante **MAPPE OFFLINE** richiede il catalogo HTTPS.
2. Vengono proposti solo gli elementi con `status: "available"` e URL di download valorizzato.
3. Prima del download viene mostrata la dimensione dichiarata.
4. Il pacchetto viene scaricato nella cartella privata dell'app `files/offline_maps`.
5. L'app controlla dimensione esatta, SHA-256, apertura SQLite, tabelle MBTiles `metadata` e `tiles`, formato `png` e presenza di tile.
6. Solo dopo la verifica il file temporaneo viene installato con sostituzione protetta dell'eventuale versione precedente.
7. L'ID della mappa scelta viene memorizzato e la stessa mappa viene riaperta al successivo avvio.

## API aggiunte a CacciaMapView

- `DownloadCatalog(url)`
- `DownloadOfflineMap(url, fileName, sha256, sizeBytes)`
- `GetOfflineMapPath(fileName)`

Eventi aggiunti:

- `catalogloaded(json)`
- `catalogerror(message)`
- `mapdownloadprogress(percent)`
- `mapdownloaded(path)`
- `mapdownloaderror(message)`

## Vincoli

- Solo URL HTTPS.
- Il catalogo deve pubblicare URL diretto, dimensione in byte e SHA-256.
- Sono accettati solo pacchetti MBTiles raster PNG.
- La disponibilità della mappa non è automatica: il download parte solo da una scelta dell'utente.
- Nessuna modifica prevista a GPS telefono, BLE, LoRa, marker, tracce o logica di squadra.
- La prima area prevista è il Lazio; resta `planned` finché l'asset MBTiles non viene creato e verificato.
