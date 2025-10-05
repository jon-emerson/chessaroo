# BlunderLab

BlunderLab is a web application that imports Chess.com games so players can capture, review, and critique their play with richer metadata than the source site provides.

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 14 + React for routing, forms, and the dashboard experience
- **Import Flow**: URL submission form that calls the backend import API and redirects to the saved game view
- **Insight Surfaces**: Dashboard cards that summarize recurring tactical issues and opening pitfalls once analysis jobs finish
- **Game Viewer**: Dynamic routes for imported games with metadata panels, critique prompts, and guidance for follow-up study sessions

### Backend
- **API**: Flask web framework with RESTful endpoints
- **Database**: PostgreSQL via SQLAlchemy models for users, games, moves, and imported game payloads
- **Chess.com Integration**: Requests client to fetch live game JSON, error handling, and metadata extraction helpers
- **Insight Pipeline**: Services designed to scan imported PGNs, label recurring tactical vulnerabilities (pins, skewers, forks, opposition), and flag opening branches with historically weak responses
- **Authentication**: Session-based auth protecting import/review endpoints

### Infrastructure
- **Cloud Platform**: AWS (Amazon Web Services)
- **Containerization**: Docker with AWS ECS Fargate
- **Load Balancing**: Application Load Balancer
- **Database**: AWS RDS PostgreSQL
- **Container Registry**: Amazon ECR
- **Infrastructure as Code**: Terraform configuration

## 🚀 Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker installed locally
- Git for version control

### Quick Deploy (CI/CD First)
1. Run `./scripts/setup.sh` once per environment to create/validate the Terraform remote state backend (S3 + DynamoDB) and apply the infrastructure.
2. Commit your changes and push to `main`. The `Deploy to Production` GitHub Actions workflow will build the container, push to ECR, run migrations, and roll ECS.

> Need an emergency/manual deploy? `./scripts/deploy.sh` still works locally, but the canonical path is the GitHub Actions workflow.

### Terraform Remote State Bootstrap
`./scripts/setup.sh` makes sure the Terraform backend exists before it touches any infrastructure. It creates (or reuses) the S3 bucket `blunderlab-tf-state` and DynamoDB table `blunderlab-tf-locks`, enables encryption/versioning, and then runs `terraform init/plan/apply`. Override the defaults with `TF_STATE_BUCKET` or `TF_STATE_LOCK_TABLE` if you need different names.

### Development
```bash
# Build and start the stack (backend + Postgres)
docker compose up --build

# Run database migrations inside the backend container
docker compose exec backend flask db upgrade

# Tail backend logs
docker compose logs -f backend
```

> The backend exits if it detects a non-container environment. Always use Docker for local work. For rare host-only tasks, export `ALLOW_NON_CONTAINER=1` before running the command (use sparingly).
> Docker Compose reads environment variables from your shell or a `.env` file in the repo root. Set `ADMIN_MASTER_PASSWORD_DEV` (and `ADMIN_MASTER_PASSWORD` if needed) before running `docker compose up`.

### Database Migrations
```bash
export FLASK_APP=backend.app:create_app
python3 -m flask db upgrade
```

`flask db upgrade` should be executed for every deploy to ensure the database schema matches the code. Generate new revisions with `python3 -m flask db migrate -m "describe change"` after updating `backend/models.py`.

### Admin Dashboard
- The admin interface lives at `/admin` and authenticates independently of normal user accounts.
- Configuration is environment-driven:
  - `APP_ENV` controls which credential is used (`development`, `staging`, or `production`).
  - Set `ADMIN_MASTER_PASSWORD_DEV` for development/staging and `ADMIN_MASTER_PASSWORD` for production.
- For local development, copy `.env.example` to `.env.local` (ignored by git), set the passwords, and ensure `APP_ENV=development`.
- In production, inject secrets via task definition / deployment pipeline (never check them into the repo).
- Run `python3 -m flask db stamp 0993f449f98a` once in existing environments before the first Alembic upgrade if the tables already exist.

### Continuous Deployment (GitHub Actions)
Pushes to `main` execute `.github/workflows/deploy.yml`, which is split into two coordinated jobs:
- **`terraform` job** – runs `terraform fmt`, `init`, `validate`, and `plan` against the remote backend (`s3://blunderlab-tf-state` with DynamoDB locking). On `main` it performs `terraform apply` and publishes the ECR repository, ECS cluster/service names, and ALB URL as job outputs.
- **`deploy` job** – consumes those outputs, builds the Docker image, pushes to ECR, runs database migrations through a one-off ECS task, and forces a new service deployment.

Configure these GitHub repository secrets before enabling the workflow:

| Secret | Description |
| --- | --- |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Credentials for the GitHub Actions deploy user (must have access to S3 state bucket, DynamoDB locks, ECR, ECS, RDS, CloudWatch, and Secrets Manager) |
| `AWS_REGION` | AWS region (e.g. `us-west-2`) |
| `ECR_REPOSITORY_URL` *(optional fallback)* | Only used if Terraform outputs are unavailable |
| `ECS_CLUSTER_NAME` *(optional fallback)* | Only used if Terraform outputs are unavailable |
| `ECS_SERVICE_NAME` *(optional fallback)* | Only used if Terraform outputs are unavailable |
| `LOAD_BALANCER_URL` *(optional fallback)* | Printed at the end of deploy if provided |

The IAM policy and bootstrap helper scripts live under `terraform/policies/`. Ensure the S3 bucket `blunderlab-tf-state` and DynamoDB table `blunderlab-tf-locks` exist before enabling the workflow, or adjust the backend block in `terraform/main.tf` if you use different names.

## 🌐 Live Application

- **URL**: http://blunderlab-tf-alb-1489853278.us-west-2.elb.amazonaws.com (runs on port 3000)
- **Focus**: Dashboard for importing Chess.com games, quick links back to saved critiques, and metadata summaries for each import
- **Backend Services**: Flask API for authentication, Chess.com ingestion, and database-backed storage
- **Note**: To deploy the latest changes, run `./scripts/deploy.sh`

## 📂 Project Structure

```
blunderlab/
├── backend/                 # Flask backend package
│   ├── __init__.py          # Package marker
│   ├── app.py               # Flask application factory and routes
│   └── models.py            # SQLAlchemy models
├── frontend/                # React + Next.js frontend
│   ├── src/app/             # Next.js 13+ app directory
│   │   ├── layout.tsx       # Root layout component
│   │   ├── page.tsx         # Homepage with game list
│   │   ├── game/[id]/       # Dynamic game routes
│   │   │   └── page.tsx     # Game viewer component
│   │   └── globals.css      # Global styles
│   ├── package.json         # Frontend dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   └── next.config.js       # Next.js configuration
├── helpers/                 # Backend helper modules
├── migrations/              # Alembic migrations
├── scripts/                 # Deployment and utility scripts
│   ├── deploy.sh            # Application deployment
│   ├── destroy.sh           # Infrastructure cleanup
│   ├── setup.sh             # Infrastructure provisioning helper
│   └── start-prod.sh        # Container entrypoint (gunicorn + Next.js)
├── terraform/               # Terraform configuration
│   ├── main.tf              # Core infrastructure with VPC
│   ├── ecs.tf               # ECS and container resources
│   ├── rds.tf               # PostgreSQL RDS database
│   ├── variables.tf         # Input variables
│   └── outputs.tf           # Output values
├── Dockerfile               # Production multi-stage container
├── docker-compose.yml       # Development stack
├── requirements.txt         # Python dependencies
└── README.md                # This file
```
