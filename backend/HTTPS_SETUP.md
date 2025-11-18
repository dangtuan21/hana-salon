# HTTPS Setup Guide

This guide explains how to enable HTTPS support for the Hana AI Backend API.

## Quick Start

The server supports both HTTP and HTTPS simultaneously:

- **HTTP**: `http://localhost:8060`
- **HTTPS**: `https://localhost:8443` (when enabled)

## Enable HTTPS

### Method 1: Environment Variable
```bash
ENABLE_HTTPS=true npm run dev
```

### Method 2: Update .env file
```bash
# Add to your .env file
ENABLE_HTTPS=true
HTTPS_PORT=8443
```

## SSL Certificates

### Development (Self-Signed Certificates)

Self-signed certificates are automatically generated in the `ssl/` directory:
- `ssl/certificate.pem` - SSL certificate
- `ssl/private-key.pem` - Private key

**Note**: Browsers will show security warnings for self-signed certificates. This is normal for development.

### Production (Valid SSL Certificates)

For production, replace the self-signed certificates with valid ones:

1. **Let's Encrypt** (Free):
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/certificate.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/private-key.pem
```

2. **Commercial SSL Certificate**:
   - Purchase from a Certificate Authority (CA)
   - Place certificate in `ssl/certificate.pem`
   - Place private key in `ssl/private-key.pem`

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ENABLE_HTTPS` | `false` | Enable HTTPS server |
| `HTTPS_PORT` | `8443` | HTTPS server port |
| `PORT` | `8060` | HTTP server port |

## Security Features

### CORS Support
Both HTTP and HTTPS origins are supported:
- `http://localhost:8060`
- `https://localhost:8443`
- Custom origins via `CORS_ORIGIN` environment variable

### Helmet Security
- Content Security Policy (CSP)
- HTTP Strict Transport Security (HSTS)
- X-Frame-Options protection
- XSS protection

## Testing HTTPS

### cURL Commands
```bash
# Test HTTP
curl http://localhost:8060/api/health

# Test HTTPS (ignore self-signed certificate warnings)
curl -k https://localhost:8443/api/health

# Test HTTPS with certificate verification (production)
curl https://yourdomain.com:8443/api/health
```

### Browser Access
- **HTTP Swagger UI**: `http://localhost:8060/api-docs`
- **HTTPS Swagger UI**: `https://localhost:8443/api-docs`

**Note**: For self-signed certificates, click "Advanced" → "Proceed to localhost (unsafe)" in your browser.

## Troubleshooting

### Certificate Issues
```bash
# Regenerate self-signed certificates
openssl req -x509 -newkey rsa:4096 -keyout ssl/private-key.pem -out ssl/certificate.pem -days 365 -nodes -subj "/C=US/ST=CA/L=San Francisco/O=Hana AI/OU=Development/CN=localhost"
```

### Port Conflicts
```bash
# Check what's using the ports
lsof -i :8060
lsof -i :8443

# Kill conflicting processes
sudo kill -9 <PID>
```

### CORS Issues
Add your domain to the CORS origins:
```bash
CORS_ORIGIN=https://yourdomain.com,https://localhost:8443
```

## Production Deployment

### Docker with HTTPS
```dockerfile
# Mount SSL certificates
COPY ssl/ /app/ssl/
ENV ENABLE_HTTPS=true
ENV HTTPS_PORT=443
EXPOSE 80 443
```

### Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.pem;
    ssl_certificate_key /path/to/private-key.pem;
    
    location / {
        proxy_pass http://localhost:8060;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Load Balancer SSL Termination
If using a load balancer (AWS ALB, Cloudflare, etc.):
```bash
# Disable HTTPS on the application
ENABLE_HTTPS=false
# Let the load balancer handle SSL
```

## Security Best Practices

1. **Never commit SSL certificates** to version control
2. **Use strong cipher suites** in production
3. **Enable HSTS** for production domains
4. **Regular certificate renewal** (Let's Encrypt auto-renewal)
5. **Monitor certificate expiration**

## API Endpoints (Both HTTP & HTTPS)

| Endpoint | HTTP | HTTPS |
|----------|------|-------|
| Health Check | `http://localhost:8060/api/health` | `https://localhost:8443/api/health` |
| Services API | `http://localhost:8060/api/services` | `https://localhost:8443/api/services` |
| Swagger UI | `http://localhost:8060/api-docs` | `https://localhost:8443/api-docs` |

Both servers run simultaneously when HTTPS is enabled, providing maximum flexibility for development and production scenarios.
