# Docker release-prep rules

Apply when `Dockerfile` or `docker-compose.yml` (or `.yaml`) exists at repo root.

## Checks

### 1. Dockerfile changed without image tag bump — WARNING

If `Dockerfile` is modified in the diff and the project has a tagged-image
convention (e.g., `image:` line in `docker-compose.yml`, or a `VERSION` file, or
a CI tag step), check whether the tag/version was also bumped in this branch.

If not → **WARNING**: "`Dockerfile` changed but image tag not bumped — verify cache-bust intentional."

### 2. New compose service env without `.env.example` — BLOCK

For each `environment:` or `env_file:` entry added to `docker-compose.yml` in the
diff, ensure referenced keys are declared in `.env.example`.

If a key is referenced (e.g., `${API_KEY}`) and not in `.env.example` →
**BLOCK**: "Compose env `<KEY>` undocumented."

### 3. FROM base image bumped major version — WARNING

If the diff changes `FROM <image>:<tag>` and the major version differs (e.g.,
`node:20-alpine` → `node:22-alpine`, `python:3.11` → `python:3.12`) → **WARNING**:
"Base image bumped — verify CI runner and prod host compatibility."

### 4. Multi-stage build cache layer regression — WARNING

If a `RUN apt-get install` / `RUN apk add` / `RUN npm install` / `RUN pip install`
moved earlier in the Dockerfile such that source-changing layers now precede it →
**WARNING**: "Layer order regression — install steps after source COPY will refetch packages on every build."

## Skip if

- No Dockerfile and no docker-compose file.
