# PostgreSQL Database Service
resource "render_postgres" "hitoq_db" {
  name         = "hitoq-database"
  plan         = "standard" # or "free" for development
  region       = "oregon"   # or preferred region
  database_name = "hitoq"
  database_user = "hitoq"
}

# Backend API Service
resource "render_web_service" "hitoq_backend" {
  name               = "hitoq-backend"
  plan               = "standard" # or "free" for development
  region             = "oregon"   # or preferred region
  runtime            = "docker"
  repo_url           = var.github_repo_url
  branch             = "main"
  root_dir           = "backend"
  dockerfile_path    = "Dockerfile"
  
  # Build settings
  build_command      = ""  # Using Docker build
  start_command      = ""  # Using Docker CMD
  
  # Health check
  health_check_path  = "/health"
  
  # Auto deploy on push
  auto_deploy        = true
  
  # Environment variables
  environment_variables = {
    DATABASE_URL        = render_postgres.hitoq_db.database_url
    DB_HOST            = render_postgres.hitoq_db.host
    DB_PORT            = render_postgres.hitoq_db.port
    DB_NAME            = render_postgres.hitoq_db.database_name
    DB_USER            = render_postgres.hitoq_db.database_user
    DB_PASSWORD        = render_postgres.hitoq_db.database_password
    SECRET_KEY         = var.secret_key
    SESSION_SECRET_KEY = var.session_secret_key
    TWITTER_CLIENT_ID  = var.twitter_client_id
    TWITTER_CLIENT_SECRET = var.twitter_client_secret
    TWITTER_REDIRECT_URI = "https://api.hitoq.net/auth/callback/twitter"
    FRONTEND_URLS      = "https://hitoq.net"
    COOKIE_SECURE      = "true"
    ENVIRONMENT        = var.environment
    SENTRY_DSN         = var.sentry_dsn
    LOG_LEVEL          = "INFO"
  }
  
  # Disk storage (if needed)
  disk = {
    name       = "hitoq-backend-disk"
    size_gb    = 1
    mount_path = "/data"
  }
}

# Frontend Web Service
resource "render_web_service" "hitoq_frontend" {
  name            = "hitoq-frontend"
  plan            = "standard" # or "free" for development
  region          = "oregon"   # or preferred region
  runtime         = "docker"
  repo_url        = var.github_repo_url
  branch          = "main"
  root_dir        = "frontend"
  dockerfile_path = "Dockerfile"
  
  # Build settings
  build_command   = ""  # Using Docker build
  start_command   = ""  # Using Docker CMD
  
  # Health check
  health_check_path = "/health"
  
  # Auto deploy on push
  auto_deploy     = true
  
  # Environment variables for build time
  environment_variables = {
    PUBLIC_SENTRY_DSN    = var.public_sentry_dsn
    PUBLIC_ENVIRONMENT   = var.environment
  }
}

# Output important URLs
output "database_url" {
  description = "Database connection URL"
  value       = render_postgres.hitoq_db.database_url
  sensitive   = true
}

output "backend_url" {
  description = "Backend service URL"
  value       = render_web_service.hitoq_backend.url
}

output "frontend_url" {
  description = "Frontend service URL"
  value       = render_web_service.hitoq_frontend.url
}

output "database_host" {
  description = "Database host"
  value       = render_postgres.hitoq_db.host
}

output "database_port" {
  description = "Database port"
  value       = render_postgres.hitoq_db.port
}