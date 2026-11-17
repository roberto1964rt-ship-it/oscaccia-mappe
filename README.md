# OSCACCIA - Mappe offline

Repository dei pacchetti cartografici offline per OSCACCIA (Capo e Cacciatore/Capocaccia).

Prima area pilota: Lazio, Italia.

Il catalogo remoto è in catalog/catalog.json. I pacchetti MBTiles saranno distribuiti come asset GitHub Releases, non committati come file binari nel repository.

Il pacchetto pilota sarà dichiarato disponibile solo dopo generazione e verifica di un MBTiles raster PNG compatibile con il loader Android attuale.

I dati derivati da OpenStreetMap sono soggetti a ODbL. Attribuzione da mostrare nell'app: © OpenStreetMap contributors.

Non scaricare in massa tile raster da tile.openstreetmap.org. Generare i raster da estratti dati OSM e verificare separatamente licenze di stile, font e icone.

## Generare il pacchetto Lazio

Nel repository è presente un workflow GitHub Actions per creare il pacchetto raster MBTiles compatibile con OSCACCIA:

- aprire la scheda **Actions**;
- scegliere **Build Lazio raster MBTiles**;
- premere **Run workflow** sul branch `main`;
- attendere il completamento di tutte le fasi.

Solo al termine del workflow, dopo i controlli SQLite/PNG e la pubblicazione dell'asset GitHub Release, il catalogo passa automaticamente il Lazio da `planned` a `available`.

La generazione usa l'estratto Geofabrik Centro Italia, che include il Lazio, e un renderer OSM locale. Non vengono scaricate in massa tile dal server pubblico OSM. La copertura usa il riquadro geografico Lazio con un piccolo margine ai confini.
