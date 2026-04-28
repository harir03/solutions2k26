# IntelliCredit - Setup Guide

## Project Structure

```
/workspace
├── README.md                 # Main project documentation
├── SETUP.md                  # This file
├── frontend/                 # React/Next.js dashboard
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   │   ├── page.tsx     # Main dashboard page
│   │   │   ├── layout.tsx   # Root layout
│   │   │   └── globals.css  # Global styles
│   │   ├── components/      # Reusable components
│   │   │   ├── dashboard/   # Dashboard widgets
│   │   │   ├── layout/      # Header, Sidebar
│   │   │   └── applications/# Application cards
│   │   └── styles/          # Additional styles
│   ├── package.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   └── tsconfig.json
└── dashboard_template/       # Original template (reference)
```

## Quick Start

### Frontend Setup

```bash
cd /workspace/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit http://localhost:3000

### Backend Setup (Coming Soon)

The backend will include:
- FastAPI server
- Celery workers for parallel data processing
- PostgreSQL database
- Redis queue
- ML models (XGBoost + LightGBM)

## Dashboard Components

All components are copied from `dashboard_template` and adapted for IntelliCredit:

### Dashboard Widgets
- `StatCard` - Display key metrics (190M+ credit-invisible, etc.)
- `ProgressBarCard` - Show score distribution bars
- `DonutChartCard` - Visualize applicant breakdown by score band
- `SecurityPosture` - Overall system health

### Layout Components
- `Header` - Top navigation with branding
- `Sidebar` - Side navigation menu

### Application Components
- `ApplicationCard` - Individual applicant details
- `AddApplicationModal` - Add new applicants
- `DefenseModeModal` - System settings

## Customization

### Update Stats

Edit `/workspace/frontend/src/app/page.tsx`:

```typescript
const stats = [
  { label: 'Your Metric', value: '123', change: '+5%', isPositive: true },
]
```

### Update Score Distribution

```typescript
const scoreDistribution = [
  { name: 'Excellent (750-850)', value: 18, count: 1800 },
  { name: 'Good (650-749)', value: 27, count: 2700 },
  // ... more bands
]
```

## Deployment

### Frontend (Vercel)

```bash
cd /workspace/frontend
npm run build
vercel deploy
```

### Backend (Render)

Instructions coming soon.

## Environment Variables

Create `.env.local` in frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Submit PR

## License

MIT License
