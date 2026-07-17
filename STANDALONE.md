# Publicación autónoma

Esta versión funciona sin acceso al disco original porque `rnaseq_index.sqlite` contiene las anotaciones ITAG4.0 y los TPM ya procesados. Los archivos `quant.sf` y el GFF no son necesarios durante la consulta.

## Ejecución directa

En Windows:

```powershell
python app.py
```

o doble clic en `iniciar_windows.bat`.

En Linux/WSL:

```bash
chmod +x iniciar_linux.sh
./iniciar_linux.sh
```

Luego abre:

<http://127.0.0.1:8765>

## Publicación con enlace web

GitHub Pages no sirve esta app porque Pages solo ejecuta HTML/CSS/JS estático. Este buscador necesita un proceso Python que lea SQLite.

Para tener un link público usa Render, Railway, Fly.io o un VPS. En Render:

1. Crea un repositorio en GitHub con esta carpeta.
2. En Render selecciona **New Web Service**.
3. Elige el repositorio.
4. Si el repositorio contiene la carpeta `standalone_release/`, usa esa carpeta como **Root Directory**.
5. Selecciona Docker.
6. Usa `Dockerfile.standalone`.

El Dockerfile ya respeta la variable `PORT`, así que Render puede asignar el puerto automáticamente.

## Docker autónomo

```bash
docker compose -f docker-compose.standalone.yml up --build
```

Abre <http://localhost:8765>. El contenedor no monta ni consulta directorios del equipo anfitrión.

## Archivos mínimos

- `app.py`
- `rnaseq_index.sqlite`
- `sample_metadata.csv`
- `web/`
- `Dockerfile.standalone`
- `docker-compose.standalone.yml`
- `README.md`
- `LICENSE`

El índice pesa aproximadamente 62 MB y cabe bajo el límite de 100 MB por archivo de GitHub. Para históricos grandes conviene usar Git LFS o adjuntarlo a una GitHub Release.

## Actualización futura de datos

La reconstrucción sí requiere los `quant.sf` y el GFF:

```bash
python app.py --reindex --config config.example.json
```

Después reemplaza `rnaseq_index.sqlite` en el repositorio o en la carpeta `standalone_release/`.
