# Quick Start Guide

Get the SOW Generator Frontend up and running in 3 simple steps!

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Create environment file
cp .env.local.example .env.local

# 3. Start development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see your application!

## 📋 Prerequisites

- Node.js 18+ installed
- Backend API running on port 8080

## 🎨 What You Get

- ✅ Modern, gradient-based UI
- ✅ Responsive design (mobile & desktop)
- ✅ Real-time progress tracking
- ✅ Form validation
- ✅ Toast notifications
- ✅ Smooth animations
- ✅ Professional styling with Tailwind CSS & shadcn/ui

## 🔧 Starting the Backend

In a separate terminal, start the backend server:

```bash
cd ../
python -m src.sow_generator.server
```

The backend will run on `http://localhost:8080`

## 📖 Next Steps

1. Review [README.md](README.md) for detailed documentation
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
3. Start customizing the UI to match your brand!

## 🎯 Usage

1. **Enter Proposal Folder URL**: Paste the Google Drive link containing your proposal
2. **Enter Output Folder URL**: Paste where you want the SOW saved
3. **Click Generate**: Watch the magic happen!

## 🐛 Troubleshooting

**Port 3000 already in use?**
```bash
PORT=3001 npm run dev
```

**Can't connect to backend?**
- Ensure backend is running on port 8080
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`

## 📞 Need Help?

- Check the [README.md](README.md) for detailed info
- Review component code in `components/` directory
- Inspect API integration in `lib/api.ts`

Happy building! 🎉
