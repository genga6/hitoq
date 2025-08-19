terraform {
  cloud {
    organization = "hitoq"
    workspaces {
      name = "hitoq-production"
    }
  }

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
  }
}

variable "render_api_key" {
  description = "Render API Key"
  type        = string
  sensitive   = true
}

variable "github_repo_url" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/genga6/hitoq"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Database credentials
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}

variable "session_secret_key" {
  description = "Session secret key"
  type        = string
  sensitive   = true
}

variable "twitter_client_id" {
  description = "Twitter OAuth client ID"
  type        = string
  sensitive   = true
}

variable "twitter_client_secret" {
  description = "Twitter OAuth client secret"
  type        = string
  sensitive   = true
}

variable "sentry_dsn" {
  description = "Sentry DSN for backend"
  type        = string
  sensitive   = true
}

variable "public_sentry_dsn" {
  description = "Sentry DSN for frontend"
  type        = string
  sensitive   = true
}

# Additional database variables
variable "db_host" {
  description = "Database host"
  type        = string
}

variable "db_user" {
  description = "Database user"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "postgres"
}

variable "db_port" {
  description = "Database port"
  type        = string
  default     = "6543"
}

# Frontend configuration
variable "frontend_urls" {
  description = "Frontend URLs"
  type        = string
  default     = "https://hitoq.net"
}

variable "public_api_base_url" {
  description = "Public API base URL"
  type        = string
  default     = "https://api.hitoq.net"
}

variable "twitter_redirect_uri" {
  description = "Twitter OAuth redirect URI"
  type        = string
  default     = "https://api.hitoq.net/auth/callback/twitter"
}

# Environment settings
variable "cookie_secure" {
  description = "Cookie secure setting"
  type        = string
  default     = "true"
}

variable "log_level" {
  description = "Log level"
  type        = string
  default     = "INFO"
}

variable "public_environment" {
  description = "Public environment name"
  type        = string
  default     = "production"
}

# CORS settings
variable "cors_allow_methods" {
  description = "CORS allowed methods"
  type        = string
  default     = "GET,POST,PUT,DELETE,PATCH"
}

variable "cors_allow_headers" {
  description = "CORS allowed headers"
  type        = string
  default     = "Content-Type,Authorization,Accept"
}


# Render owner ID
variable "render_owner_id" {
  description = "Render Owner ID (username)"
  type        = string
}

provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}