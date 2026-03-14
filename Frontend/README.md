# SOW Generator Frontend

A modern, beautiful frontend for the SOW Generator application built with Next.js, TypeScript, and Tailwind CSS.

## Features

- 🎨 Modern, gradient-based UI design
- 🚀 Fast and responsive with Next.js 15
- 📱 Mobile-first responsive design
- ✨ Smooth animations with Framer Motion
- 🎯 Type-safe with TypeScript
- 🔍 Form validation with Zod and React Hook Form
- 🎭 Beautiful UI components with shadcn/ui
- 📊 Real-time progress tracking
- 🔔 Toast notifications for user feedback

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Animations**: Framer Motion
- **Form Handling**: React Hook Form + Zod
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:

```bash
npm install
```

2. Copy the environment file:

```bash
cp .env.local.example .env.local
```

3. Update the `.env.local` file with your backend API URL if different from default:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Build for production:

```bash
npm run build
```

Start production server:

```bash
npm start
```

## Project Structure

```
Frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── google-drive-input.tsx
│   └── progress-tracker.tsx
├── lib/                   # Utilities
│   ├── api.ts            # API service
│   └── utils.ts          # Helper functions
└── public/               # Static assets
```

## Usage

1. Enter the Google Drive folder URL containing your proposal documents
2. Enter the Google Drive folder URL where the generated SOW should be saved
3. Click "Generate Statement of Work"
4. Track the progress through the visual stages
5. Download or view the generated SOW when complete

## API Integration

The frontend integrates with the SOW Generator backend API running on port 8080. The API endpoints are:

- `POST /api/generate-sow` - Generate a new SOW
- `GET /api/sow-progress/:sessionId` - Get generation progress
- `GET /health` - Health check

## Customization

### Colors and Theme

Edit the CSS variables in [app/globals.css](app/globals.css) to customize the color scheme.

### Components

All UI components are in the `components/ui/` directory and can be customized as needed.

## Contributing

Contributions are welcome! Please follow the existing code style and patterns.

## License

MIT
