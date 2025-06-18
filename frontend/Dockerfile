# frontend/Dockerfile

# Stage 1: Build the React application
FROM node:18-alpine AS build-stage

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package.json package-lock.json* ./
# If you use yarn, it would be:
# COPY package.json yarn.lock ./

# Install dependencies
# Using --legacy-peer-deps as it was used before, though for a clean build it might not be needed
# if package-lock.json is up-to-date and correct.
RUN npm install --legacy-peer-deps

# Copy the rest of the application source code
COPY . .

# VITE_API_BASE_URL will be set via Nginx config or at runtime if needed differently for static build.
# For a static build, it's often best if VITE_API_BASE_URL is a relative path like /api/v1
# Our .env.production should set VITE_API_BASE_URL=/api/v1
# Ensure your build script uses the production environment variables.
# Vite typically uses .env.production for `npm run build`.
RUN npm run build

# Stage 2: Serve the built application with Nginx
FROM nginx:1.25-alpine

# Copy built assets from build-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY nginx.default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
