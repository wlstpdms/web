#!/usr/bin/env bash
set -Eeuo pipefail

# Executed on the Linux server, with configuration passed by ssh-action.
: "${COMPONENT:?}" "${DEPLOY_SHA:?}" "${RELEASE_DIR:?}"
[[ "$COMPONENT" == backend || "$COMPONENT" == frontend ]]
[[ "$DEPLOY_SHA" =~ ^[0-9a-f]{40}$ ]]
[[ "$SERVICE_PORT" =~ ^[0-9]+$ ]] && (( SERVICE_PORT > 0 && SERVICE_PORT < 65536 ))
command -v docker >/dev/null
command -v curl >/dev/null
docker info >/dev/null

name="ai02-${COMPONENT}"
image="${name}:${DEPLOY_SHA}"
docker load --input "$RELEASE_DIR/image.tar"

args=(--detach --name "$name" --restart unless-stopped)
if [[ "$COMPONENT" == backend ]]; then
    test -f /opt/ai02/backend.env
    mkdir -p /opt/ai02/data /opt/ai02/uploads
    args+=(--publish "${SERVICE_PORT}:8000" --env-file /opt/ai02/backend.env
        --mount type=bind,src=/opt/ai02/data,dst=/data
        --mount type=bind,src=/opt/ai02/uploads,dst=/opt/application/uploads)
    health_path=/openapi.json
else
    : "${BACKEND_UPSTREAM:?}"
    # Host networking lets nginx reach the backend through 127.0.0.1.
    args+=(--network host --env "FRONTEND_HTTP_PORT=$SERVICE_PORT"
        --env "BACKEND_UPSTREAM=$BACKEND_UPSTREAM")
    health_path=/
fi

had_previous=false
if docker container inspect "$name" >/dev/null 2>&1; then
    # A leftover backup indicates an interrupted deployment; do not overwrite it.
    if docker container inspect "${name}-previous" >/dev/null 2>&1; then
        echo "Resolve the existing ${name}-previous container before retrying." >&2
        exit 1
    fi
    docker stop "$name"
    docker rename "$name" "${name}-previous"
    had_previous=true
fi

rollback() {
    docker logs --tail 100 "$name" >&2 || true
    docker rm --force "$name" >/dev/null 2>&1 || true
    if "$had_previous"; then
        docker rename "${name}-previous" "$name"
        docker start "$name"
    fi
}
trap rollback ERR
docker run "${args[@]}" "$image"
healthy=false
for attempt in {1..30}; do
    if [[ "$(docker inspect --format '{{.State.Running}}' "$name")" == true ]] &&
        curl --fail --silent --output /dev/null --max-time 3 "http://127.0.0.1:${SERVICE_PORT}${health_path}"; then
        healthy=true
        break
    fi
    sleep 2
done
if ! "$healthy"; then
    echo "New container failed its HTTP startup check." >&2
    false
fi
trap - ERR
if "$had_previous"; then
    docker rm "${name}-previous"
fi
# Only remove the transferred archive; keep image tags for manual rollback.
rm -- "$RELEASE_DIR/image.tar"
echo "Deployed $image successfully."
