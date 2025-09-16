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

**Phase 2: Chess Engine** 🔄 (Next)
- [ ] Chess game logic implementation
- [ ] Move validation and game rules
- [ ] Game state management
- [ ] Basic single-player interface

**Phase 3: Database Integration** 📋 (Planned)
- [ ] PostgreSQL database setup on AWS RDS
- [ ] Game persistence models
- [ ] User authentication system
- [ ] Game history and statistics

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
| **Frontend** | HTML/CSS/JavaScript + Yjs | User interface and real-time sync |
| **Backend** | Flask + Gunicorn | Web API and game logic |
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
# Run locally with Docker Compose (recommended)
docker-compose up

# Or run with direct Docker
docker build -t chessaroo .
docker run -p 8000:8000 chessaroo

# Or run Flask directly
pip install -r requirements.txt
python app.py
```

## 🌐 Live Application

**Current Status**: Foundation deployment
- **URL**: http://chessaroo-tf-alb-1489853278.us-west-2.elb.amazonaws.com
- **Status**: Basic Chessaroo application foundation ready for chess engine development
- **Note**: To deploy the latest changes, run `./scripts/deploy.sh`

## 📂 Project Structure

```
chessaroo/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Local development setup
├── terraform/               # Terraform configuration
│   ├── main.tf              # Core infrastructure
│   ├── ecs.tf               # ECS and container resources
│   ├── variables.tf         # Input variables
│   └── outputs.tf           # Output values
├── scripts/                 # Deployment automation
│   ├── setup.sh             # Infrastructure setup
│   ├── deploy.sh            # Application deployment
│   └── destroy.sh           # Infrastructure cleanup
└── README.md               # This file
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