terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "image" {
  description = "Imagem do container no Artifact Registry"
  type        = string
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# APIs necessárias
resource "google_project_service" "apis" {
  for_each           = toset(["run.googleapis.com", "aiplatform.googleapis.com", "artifactregistry.googleapis.com"])
  service            = each.value
  disable_on_destroy = false
}

# Conta de serviço dedicada (menor privilégio)
resource "google_service_account" "agent" {
  account_id   = "support-agent-sa"
  display_name = "Agente de triagem de chamados"
}

resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

# Serviço no Cloud Run (privado: exige autenticação IAM)
resource "google_cloud_run_v2_service" "agent" {
  name     = "support-agent"
  location = var.region

  template {
    service_account = google_service_account.agent.email
    containers {
      image = var.image
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  depends_on = [google_project_service.apis]
}

output "url" {
  value = google_cloud_run_v2_service.agent.uri
}
