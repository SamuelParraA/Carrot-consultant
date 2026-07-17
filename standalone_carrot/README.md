# Consultor TPM · raíces de zanahoria

Aplicación standalone para explorar la expresión génica de *Daucus carota* (RefSeq; BioProject PRJNA626692) procesada por Peipers-RNAseq.

## Diseño experimental

Tres condiciones biológicas, cada una con tres réplicas:

- Raíz desarrollada en oscuridad durante 4 semanas.
- Raíz desarrollada en oscuridad durante 8 semanas.
- Sección de raíz expuesta a luz a las 8 semanas.

La aplicación permite buscar por GeneID, identificador `LOC`, alias, producto RefSeq y nombres canónicos procedentes del Knowledge Engine. Muestra TPM por réplica, promedios por condición, desviación estándar, perfiles, heatmap y exportaciones CSV, Excel, SVG, PNG y PDF.

## Uso local

El índice `rnaseq_index.sqlite` ya está incluido.

```powershell
python app.py
```

Abre `http://127.0.0.1:8765`.

## Reconstruir el índice

Solo en el equipo que contiene el proyecto Peipers-RNAseq en `I:\transcriptomica\daucus_carota`:

```powershell
python build_carrot_index.py
```

El índice se construye a partir de `Annotation_master.tsv`, `Aliases.tsv`, `Gene_TPM.tsv`, la metadata de muestras y el panel de conocimiento.

## Publicación en Render

Publica el contenido de esta carpeta en un repositorio GitHub. Crea un **Web Service** en Render y selecciona Docker; `render.yaml` referencia `Dockerfile.standalone`. Render asigna automáticamente la variable `PORT`. La aplicación publicada es autocontenida y no requiere acceso a `I:`.
