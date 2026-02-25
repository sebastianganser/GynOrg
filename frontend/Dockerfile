# ---- Build Stage ----
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install dependencies (using clean install for reproducible builds)
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the Vite application
# When building for production with Docker, APIs are usually mapped via proxy
RUN npm run build

# ---- Production Stage ----
FROM nginx:alpine

# Copy custom NGINX configuration
# If we need internal routing (e.g. React Router), we must configure Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts to the NGINX html directory
COPY --from=build /app/dist /usr/share/nginx/html

# Fix permissions to avoid 403 Forbidden errors on static assets (like vite.svg)
RUN chmod -R 755 /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
