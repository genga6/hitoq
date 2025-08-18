# PostgreSQL Database Service
resource "render_postgres" "hitoq_db" {
  name         = "hitoq-database"
  plan         = "standard" # or "free" for development
  region       = "oregon"   # or preferred region
  database_name = "hitoq"
  database_user = "hitoq"
  version      = "16"       # PostgreSQL version
}

# Backend API Service
resource "render_web_service" "hitoq_backend" {
  name               = "hitoq-backend"
  plan               = "standard" # or "free" for development
  region             = "oregon"   # or preferred region
  
  runtime_source = {
    docker = {
      repo_url        = var.github_repo_url
      branch          = "main"
      build_filter = {
        paths = ["backend/**"]
      }
      dockerfile_path = "backend/Dockerfile"
    }
  }
  
  # Environment variables
  env_vars = {
    # Database configuration (using external DB variables if provided, otherwise Render PostgreSQL)
    DATABASE_URL        = var.db_host != "" ? "postgresql://${var.db_user}:${var.db_password}@${var.db_host}:${var.db_port}/${var.db_name}" : render_postgres.hitoq_db.database_url
    DB_HOST            = var.db_host != "" ? var.db_host : render_postgres.hitoq_db.host
    DB_PORT            = var.db_host != "" ? var.db_port : render_postgres.hitoq_db.port
    DB_NAME            = var.db_host != "" ? var.db_name : render_postgres.hitoq_db.database_name
    DB_USER            = var.db_host != "" ? var.db_user : render_postgres.hitoq_db.database_user
    DB_PASSWORD        = var.db_host != "" ? var.db_password : render_postgres.hitoq_db.database_password
    
    # Application security
    SECRET_KEY         = var.secret_key
    SESSION_SECRET_KEY = var.session_secret_key
    
    # Twitter OAuth configuration
    TWITTER_CLIENT_ID  = var.twitter_client_id
    TWITTER_CLIENT_SECRET = var.twitter_client_secret
    TWITTER_REDIRECT_URI = var.twitter_redirect_uri
    
    # Frontend configuration
    FRONTEND_URLS      = var.frontend_urls
    
    # Environment settings
    COOKIE_SECURE      = var.cookie_secure
    ENVIRONMENT        = var.environment
    LOG_LEVEL          = var.log_level
    
    # Monitoring and logging
    SENTRY_DSN         = var.sentry_dsn
    
    # CORS settings
    CORS_ALLOW_METHODS = var.cors_allow_methods
    CORS_ALLOW_HEADERS = var.cors_allow_headers
  }
}

# Frontend Web Service
resource "render_web_service" "hitoq_frontend" {
  name            = "hitoq-frontend"
  plan            = "standard" # or "free" for development
  region          = "oregon"   # or preferred region
  
  runtime_source = {
    docker = {
      repo_url        = var.github_repo_url
      branch          = "main"
      build_filter = {
        paths = ["frontend/**"]
      }
      dockerfile_path = "frontend/Dockerfile"
    }
  }
  
  # Environment variables for build time
  env_vars = {
    PUBLIC_SENTRY_DSN    = var.public_sentry_dsn
    PUBLIC_ENVIRONMENT   = var.public_environment
    PUBLIC_API_BASE_URL  = var.public_api_base_url
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