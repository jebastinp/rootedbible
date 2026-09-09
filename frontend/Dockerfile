FROM node:20-alpine AS build
WORKDIR /app

# Vite bakes VITE_* vars into the build at build time - pass the deployed
# backend's public URL here (e.g. https://rooted-backend.up.railway.app/api/v1)
# when deploying frontend and backend as separate services (Railway, etc.).
# Leave unset for same-origin deploys where nginx proxies /api/ locally.
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Railway (and most PaaS hosts) assign the listen port dynamically via
# $PORT - the official nginx image's entrypoint envsubst's it into the
# template above at container start. Default to 80 for local docker compose.
ENV PORT=80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
