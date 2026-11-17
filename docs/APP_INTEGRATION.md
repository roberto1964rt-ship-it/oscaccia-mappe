# Integrazione app OSCACCIA

Le pagine Capo e Cacciatore/Capocaccia usano lo stesso catalogo remoto:

`https://raw.githubusercontent.com/roberto1964rt-ship-it/oscaccia-mappe/main/catalog/catalog.json`

## Pagina elenco mappe

Il pulsante **MAPPE OFFLINE** apre una pagina dedicata, realizzata nel modulo `app/B4XPageOfflineMaps.bas`. La pagina mostra tutte le aree del catalogo in un elenco a due righe con nome, Paese/regione e stato.

- `status: planned`: visibile come **IN PREPARAZIONE**; non avvia download.
- `status: available` con URL HTTPS: selezionabile e inoltra al flusso di download.

I progetti Capo e Cacciatore usano ID pagina diversi (`offlinemaps_capo` e `offlinemaps_cacciatore`) per evitare collisioni se i moduli convivono nello stesso progetto.

## Flusso di download

1. Il catalogo viene letto via HTTPS.
2. Prima del download viene mostrata la dimensione dichiarata.
3. Il pacchetto viene scaricato nella cartella privata dell'app `files/offline_maps`.
4. L'app controlla dimensione esatta, SHA-256, apertura SQLite, tabelle MBTiles `metadata` e `tiles`, formato `png` e presenza di tile.
5. Solo dopo la verifica il file viene installato e l'ID della mappa viene memorizzato per il successivo avvio.

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
- Il download parte solo dopo una selezione esplicita dell'utente.
- Nessuna modifica prevista a GPS telefono, BLE, LoRa, marker, tracce o logica di squadra.
- Il Lazio resta `planned` finché l'asset MBTiles non viene creato e verificato.
