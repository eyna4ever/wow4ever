# Static integration: no npm dependencies, database or accounts required.
FROM node:24-bookworm-slim AS build
WORKDIR /app
COPY . .
RUN node scripts/build-static.mjs
FROM nginxinc/nginx-unprivileged:1.28-alpine
COPY --from=build --chown=101:101 /app/dist /usr/share/nginx/html
EXPOSE 8080
