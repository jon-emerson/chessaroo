# Chessaroo

A multiplayer chess web application built with real-time collaboration using conflict-free replicated data types (CRDTs).

## 🎯 Project Vision

Chessaroo aims to provide a seamless multiplayer chess experience with real-time synchronization, allowing players to engage in chess matches with instant move updates and conflict resolution.

## 🏗️ Architecture

### Frontend
- **Real-time Collaboration**: [Yjs](https://yjs.dev/) for conflict-free replicated data types (CRDTs)
- **Framework**: Modern web technologies for responsive chess interface
- **Features**: Live move synchronization, game state persistence, spectator mode

### Backend
- **API**: Flask web framework with RESTful endpoints
- **Database**: PostgreSQL for game persistence and user management
- **Real-time**: WebSocket connections for live game updates
- **Authentication**: User accounts and game session management

### Infrastructure
- **Cloud Platform**: AWS (Amazon Web Services)
- **Containerization**: Docker with AWS ECS Fargate
- **Load Balancing**: Application Load Balancer
- **Database**: AWS RDS PostgreSQL
- **Container Registry**: Amazon ECR
- **Infrastructure as Code**: Terraform configuration

## 🚀 Current Status

**Phase 1: Foundation** ✅
- [x] Basic Flask application structure
- [x] Docker containerization
- [x] AWS ECS deployment pipeline
- [x] Terraform infrastructure configuration
- [x] CI/CD deployment scripts

**Phase 2: Chess Engine** ✅
- [x] Chess game logic implementation (using python-chess)
- [x] Move validation and game rules
- [x] Game state management with FEN notation
- [x] Interactive chess board interface
- [x] Move history display and navigation

**Phase 3: Database Integration** ✅
- [x] PostgreSQL database setup on AWS RDS
- [x] Game persistence models (games and moves tables)
- [x] Algebraic notation storage
- [x] Game history and move reconstruction
- [ ] User authentication system

**Phase 4: Real-time Multiplayer** 📋 (Planned)
- [ ] Yjs integration for CRDT-based synchronization
- [ ] WebSocket connections for live updates
- [ ] Multiplayer game rooms
- [ ] Spectator mode and game sharing

**Phase 5: Enhanced Features** 📋 (Future)
- [ ] Advanced chess features (timers, ratings, tournaments)
- [ ] Mobile responsiveness
- [ ] Game analysis and replay
- [ ] Social features and friend systems

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React + Next.js + TypeScript | Modern interactive chess interface |
| **Backend** | Flask + Gunicorn | RESTful API and game logic |
| **Database** | PostgreSQL | Data persistence |
| **CRDT Library** | Yjs | Conflict-free replication |
| **Containerization** | Docker | Application packaging |
| **Orchestration** | AWS ECS Fargate | Container management |
| **Load Balancer** | AWS ALB | Traffic distribution |
| **Database Hosting** | AWS RDS | Managed PostgreSQL |
| **Container Registry** | AWS ECR | Docker image storage |
| **Infrastructure** | Terraform | Infrastructure as Code |

## 🚀 Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker installed locally
- Git for version control

### Quick Deploy
```bash
# Setup AWS infrastructure
./scripts/setup.sh

# Deploy application
./scripts/deploy.sh
```

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
Every push to `main` triggers `.github/workflows/deploy.yml`, which builds the Docker image, pushes to ECR, runs migrations, and forces a new ECS deployment. Configure these GitHub repository secrets before enabling the workflow:

| Secret | Description |
| --- | --- |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Credentials for the GitHub Actions deploy user |
| `AWS_REGION` | AWS region (e.g. `us-west-2`) |
| `ECR_REPOSITORY_URL` | Full repository URI (`1234567890.dkr.ecr.us-west-2.amazonaws.com/chessaroo-tf`) |
| `ECS_CLUSTER_NAME` | Name of the ECS cluster |
| `ECS_SERVICE_NAME` | Name of the ECS service |
| `LOAD_BALANCER_URL` *(optional)* | Production URL to print after deploy |

The IAM policy and setup helper scripts live under `terraform/policies/`.

## 🌐 Live Application

**Current Status**: Modern React chess application
- **URL**: http://chessaroo-tf-alb-1489853278.us-west-2.elb.amazonaws.com (runs on port 3000)
- **Status**: React + Next.js frontend with Flask API backend and PostgreSQL database
- **Features**: Modern TypeScript interface, React hooks, interactive chess board, move navigation
- **Note**: To deploy the latest changes, run `./scripts/deploy.sh`

## 📂 Project Structure

```
chessaroo/
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

## 🤝 Contributing

This project is in active development. Contributions and suggestions are welcome as we build towards the full multiplayer chess experience.

## 📋 Roadmap

1. **Chess Engine Development**: Implement core chess logic and validation
2. **Database Integration**: Add PostgreSQL with game and user models
3. **Real-time Sync**: Integrate Yjs for multiplayer synchronization
4. **UI/UX Enhancement**: Build intuitive chess interface
5. **Advanced Features**: Add tournaments, ratings, and social features

---

*Built with ❤️ using modern web technologies and AWS cloud infrastructure*
