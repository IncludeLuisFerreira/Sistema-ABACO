FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

ARG CACHE_BUST=1
COPY . .
RUN npm run build -- --configuration production

FROM nginx:stable-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
