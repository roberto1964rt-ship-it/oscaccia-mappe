# Generazione pacchetto Lazio

Il workflow GitHub Actions `.github/workflows/build-lazio-raster.yml` costruisce il pacchetto raster MBTiles compatibile con il loader osmdroid in CacciaMapView.

## Fonte

Il workflow scarica l'estratto PBF Geofabrik Centro Italia:

`https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf`

Il file Centro è usato come sorgente perché include il Lazio; la generazione delle tile è limitata al rettangolo geografico dichiarato nello script. È previsto un piccolo margine oltre il confine regionale per evitare che strade e riferimenti si interrompano esattamente sul limite. Il pacchetto resta destinato alla regione Lazio e dintorni immediati.

## Rendering e formato

Il PBF viene importato nel renderer OSM Carto del container `overv/openstreetmap-tile-server`. Le tile vengono richieste al server locale, non al server pubblico `tile.openstreetmap.org`, e raccolte in MBTiles raster PNG con schema TMS.

Zoom iniziale: 7-15. Se l'asset supera il margine prudenziale di dimensione, lo script riduce il livello massimo di zoom. Il limite GitHub per un singolo asset Release è 2 GiB.

## Verifiche

Lo script verifica:
- apertura SQLite e `PRAGMA integrity_check`;
- metadata MBTiles con `format=png`;
- presenza di tile e firma PNG;
- dimensioni dei tile 256x256;
- calcolo SHA-256 e dimensione finale.

Solo dopo il caricamento dell'asset Release il workflow imposta la voce `it-lazio` del catalogo a `available`.

## Attribuzione

Mostrare nell'app e mantenere nei metadata: `© OpenStreetMap contributors`. I dati OpenStreetMap sono distribuiti sotto ODbL. Il rendering usa lo stile OSM Carto incluso nel tile server; conservare anche le informazioni di licenza dello stile e delle relative risorse.

## Ripetizione

Il workflow è avviabile manualmente da Actions oppure quando cambia il suo file/script nel branch main. Versione del primo pacchetto: `1.0.0`.
