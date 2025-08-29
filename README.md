# SprintSync

A modern FastAPI-based project management and sprint tracking application with AI-powered suggestions.

## 🚀 Features

- **FastAPI Backend**: High-performance, modern Python web framework
- **PostgreSQL Database**: Robust relational database with SQLAlchemy ORM
- **AI Integration**: Smart suggestions and automation capabilities
- **Docker Support**: Easy deployment and development setup
- **Database Migrations**: Alembic for seamless schema management
- **Modern Python**: Built with Python 3.12+ and type hints

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.12+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Package Manager**: UV (fast Python package manager)
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT with PyJWT
- **Cloud**: AWS SDK (Boto3) integration

## 📦 Dependencies

- `fastapi` - Modern web framework for APIs
- `sqlalchemy` - Database ORM and toolkit
- `psycopg2-binary` - PostgreSQL adapter
- `alembic` - Database migration tool
- `uvicorn` - ASGI server
- `pydantic` - Data validation and parsing
- `pyjwt` - JSON Web Token implementation
- `cryptography` - Cryptographic recipes and primitives
- `boto3` - AWS SDK for Python
- `cachetools` - Extensible memoizing collections

## 🚦 Quick Start

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- UV package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dwij-v/sprint-sync.git
   cd sprint-sync
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Start the database**
   ```bash
   make docker-up
   ```

4. **Setup the database**
   ```bash
   make db-setup
   ```

5. **Run the development server**
   ```bash
   make dev
   ```

The API will be available at `http://localhost:8000`

## 📋 Available Commands

Use `make help` to see all available commands:

- `make dev` - Run the application in development mode
- `make docker-up` - Start services with Docker Compose
- `make docker-down` - Stop Docker services
- `make db-setup` - Setup database (run migrations)
- `make db-migrate` - Create new database migration
- `make db-reset` - Reset database (drop and recreate)
- `make test` - Run tests
- `make clean` - Clean up cache and temporary files

## 🗃️ Project Structure

```
sprintsync/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── controller/          # API controllers
│   ├── db/
│   │   └── entities.py      # Database models
│   ├── middleware/          # Custom middleware
│   ├── models/              # Pydantic models
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── repository/          # Data access layer
│   ├── routes/              # API routes
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
├── docker-compose.yml       # Docker services configuration
├── Makefile                 # Development commands
├── pyproject.toml          # Project configuration and dependencies
└── README.md               # This file
```

## 🗄️ Database

The application uses PostgreSQL as the primary database with the following configuration:

- **Host**: localhost
- **Port**: 5432
- **Database**: sprint_sync
- **Username**: postgres
- **Password**: postgres

### Database Models

- **User**: User management and authentication
- **AiSuggestion**: AI-powered suggestions and prompts
- **AiPrompts**: Template prompts for AI interactions

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sprint_sync
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🐳 Docker Development

The project includes Docker Compose for easy development setup:

```bash
# Start all services
make docker-up

# Stop all services
make docker-down

# View logs
docker compose logs -f
```

## 🧪 Testing

Run tests with:

```bash
make test
```

## 📊 API Documentation

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health-check`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have any questions or need help, please open an issue in the GitHub repository.

---

**Built with ❤️ using FastAPI and modern Python tooling**