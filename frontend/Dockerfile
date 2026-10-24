# ==============================================================================
# WindWise UK — Frontend Multi-Stage Dockerfile
# Stage 1: Build the Vite React application
# Stage 2: Serve production assets with Nginx
# ==============================================================================

# Stage 1: Build
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package descriptors
COPY package*.json ./

# Install all dependencies (including devDependencies required for Vite build)
RUN npm install

# Copy application source code
COPY index.html ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY public/ public/
COPY src/ src/

# Set VITE_API_BASE_URL to empty string by default so browser makes relative requests to Nginx
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build production bundle to /app/dist
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:alpine

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with SPA routing and /api/ reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port 80
EXPOSE 80

# Health check to ensure Nginx is serving content
HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
