# Workflow di generazione e pubblicazione MBTiles

## Area pilota

Lazio, Italia. Il pacchetto previsto e' raster MBTiles con tile PNG, perche' il loader Android esistente usa MBTiles raster e non vector tiles.

## Dati sorgente

1. Scaricare un estratto OSM regionale da un fornitore di estratti, ad esempio Geofabrik.
2. Conservare fonte, data di estrazione e checksum del file sorgente.
3. Verificare licenza ODbL e obblighi di attribuzione.

Non effettuare download massivo di tile raster dal server pubblico tile.openstreetmap.org.

## Rendering

Usare un renderer OSM che produca MBTiles raster PNG (ad esempio una pipeline basata su Mapnik/renderd o uno strumento equivalente). Registrare versione del renderer, stile, font e icone. Verificare le licenze dello stile e di tutte le risorse.

## Verifica obbligatoria

Prima della release verificare:
- il file si apre come database SQLite;
- sono presenti le tabelle MBTiles metadata e tiles;
- metadata.format e' png;
- bounds e livelli zoom coprono l'area prevista;
- i tile sono immagini PNG valide;
- la mappa e' leggibile ai livelli min/max dichiarati;
- dimensione e SHA-256 sono calcolati sul file finale.

## Pubblicazione

1. Creare una GitHub Release con tag versione, ad esempio it-lazio-v1.0.0.
2. Caricare il file .mbtiles come asset della release.
3. Copiare l'URL diretto dell'asset, dimensione e SHA-256 in catalog/catalog.json.
4. Cambiare status in available solo dopo aver scaricato nuovamente l'asset e verificato il checksum.

## Consumo dall'app

L'app deve:
- leggere il catalogo HTTPS;
- mostrare nome, Paese/regione, versione e dimensione;
- consentire download esplicito dell'utente;
- scrivere prima su un file temporaneo;
- verificare dimensione e SHA-256;
- rinominare atomicamente il file verificato;
- mantenere disponibile l'eventuale versione precedente fino al completamento della sostituzione;
- caricare MBTiles locale tramite il loader esistente.

Download e caricamento offline non devono attivarsi automaticamente all'avvio e non devono modificare GPS, BLE, LoRa o marker.
