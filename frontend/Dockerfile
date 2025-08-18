# Multi-stage build for production-ready SvelteKit frontend
FROM node:18-alpine AS builder

# Build arguments for environment variables
ARG PUBLIC_API_BASE_URL="http://localhost:8000"
ARG PUBLIC_SENTRY_DSN=""
ARG PUBLIC_ENVIRONMENT="production"

# Set environment variables for SvelteKit build
ENV PUBLIC_API_BASE_URL=$PUBLIC_API_BASE_URL
ENV PUBLIC_SENTRY_DSN=$PUBLIC_SENTRY_DSN
ENV PUBLIC_ENVIRONMENT=$PUBLIC_ENVIRONMENT

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm run build

# Production stage with Node.js
FROM node:18-alpine AS production

# Install pnpm in production stage
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-lock.yaml ./pnpm-lock.yaml

# Install only production dependencies
RUN pnpm install --prod --frozen-lockfile

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); }).on('error', () => process.exit(1));"

# Expose port
EXPOSE 3000

# Start SvelteKit server
CMD ["node", "build"]