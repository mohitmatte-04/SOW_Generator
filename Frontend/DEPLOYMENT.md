# Deployment Guide

This guide explains how to deploy the SOW Generator Frontend.

## Running Locally

### Development Mode

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

```bash
# Build the application
npm run build

# Start the production server
npm start
```

## Environment Variables

Create a `.env.local` file in the Frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

For production, update this to your production API URL:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Backend Integration

The frontend expects the backend API to be running. To start the backend:

```bash
cd /home/mohitmatte/Sow-generator/SOW_Generator
python -m src.sow_generator.server
```

The backend should be running on `http://localhost:8080`

## Deployment Options

### Option 1: Vercel (Recommended)

Vercel is the easiest way to deploy Next.js applications:

1. Push your code to GitHub
2. Import the project on [Vercel](https://vercel.com)
3. Set the root directory to `SOW_Generator/Frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy!

### Option 2: Docker

Create a `Dockerfile` in the Frontend directory:

```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package*.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

Build and run:

```bash
docker build -t sow-generator-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-api:8080 sow-generator-frontend
```

### Option 3: Static Hosting

For static hosting (Netlify, AWS S3, etc.):

```bash
npm run build
```

Then deploy the `.next` directory.

## CORS Configuration

Make sure your backend allows requests from your frontend domain. Update the backend's CORS settings in the `.env` file:

```
ALLOWED_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]
```

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, you can specify a different port:

```bash
PORT=3001 npm run dev
```

### API Connection Issues

1. Verify the backend is running on port 8080
2. Check the `NEXT_PUBLIC_API_URL` environment variable
3. Ensure CORS is properly configured on the backend
4. Check browser console for network errors

### Build Errors

If you encounter build errors:

1. Delete `.next` and `node_modules` directories
2. Run `npm install` again
3. Try building with `npm run build`

## Performance Optimization

The application includes:

- Automatic code splitting
- Image optimization
- Font optimization with next/font
- Lazy loading of components
- Production-ready animations

## Monitoring

Consider adding monitoring tools:

- [Vercel Analytics](https://vercel.com/analytics) (if using Vercel)
- Google Analytics
- Sentry for error tracking

## Security

- Never commit `.env.local` files
- Always use HTTPS in production
- Keep dependencies updated: `npm audit fix`
- Implement rate limiting on the backend
