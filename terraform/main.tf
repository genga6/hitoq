terraform {
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
  default     = "https://github.com/your-username/hitoq"
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

provider "render" {
  api_key = var.render_api_key
}