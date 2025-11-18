# Hana AI Backend

A robust Node.js + Express + TypeScript backend for the Hana AI salon booking system.

## 🚀 Features

- **TypeScript**: Full type safety and modern JavaScript features
- **Express.js**: Fast, unopinionated web framework
- **Security**: Helmet, CORS, rate limiting, and input validation
- **Logging**: Winston for structured logging
- **Error Handling**: Centralized error handling with proper HTTP status codes
- **Health Checks**: Comprehensive health, readiness, and liveness endpoints
- **Development**: Hot reload with nodemon and ts-node

## 📁 Project Structure

```
backend/
├── src/
│   ├── controllers/     # Request handlers
│   ├── middleware/      # Custom middleware
│   ├── routes/          # Route definitions
│   ├── services/        # Business logic
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   └── server.ts        # Main server file
├── dist/                # Compiled JavaScript (generated)
├── logs/                # Log files (generated)
├── package.json
├── tsconfig.json
└── README.md
```

## 🛠️ Setup

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

### Development

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint
npm run lint:fix
```

## 🌐 API Endpoints

### Health Checks
- `GET /api/health` - Comprehensive health check
- `GET /api/ready` - Readiness probe for Kubernetes
- `GET /api/live` - Liveness probe for Kubernetes

### API Info
- `GET /api/` - API information and available endpoints

## 🔧 Configuration

Environment variables (see `.env.example`):

- `NODE_ENV` - Environment (development/production)
- `PORT` - Server port (default: 3060)
- `HOST` - Server host (default: localhost)
- `API_PREFIX` - API route prefix (default: /api)
- `CORS_ORIGIN` - Allowed CORS origin
- `RATE_LIMIT_WINDOW_MS` - Rate limiting window
- `RATE_LIMIT_MAX_REQUESTS` - Max requests per window

## 🚀 Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t hana-ai-backend .

# Run container
docker run -p 3060:3060 --env-file .env hana-ai-backend
```

### Manual Deployment

```bash
# Build the application
npm run build

# Start the production server
npm start
```

## 📊 Monitoring

The backend includes comprehensive logging and health check endpoints:

- **Health Check**: `/api/health` - Returns service status, uptime, and version
- **Readiness**: `/api/ready` - Kubernetes readiness probe
- **Liveness**: `/api/live` - Kubernetes liveness probe

## 🔒 Security Features

- **Helmet**: Security headers
- **CORS**: Cross-origin resource sharing
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Joi schema validation
- **Error Handling**: No sensitive data leakage

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch
```

## 📝 Logging

Logs are written to:
- `logs/combined.log` - All logs
- `logs/error.log` - Error logs only
- Console (development only)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
