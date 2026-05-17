# Base stage for dependencies
FROM node:20-slim AS base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Development stage (used for hot-reloading)
FROM base AS dev
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# Build stage (compiles static files)
FROM base AS build
RUN npm run build

# Production stage (serves via Nginx)
FROM nginx:stable-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
