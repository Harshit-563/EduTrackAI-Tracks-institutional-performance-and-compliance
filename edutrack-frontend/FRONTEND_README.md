# EduTrack Frontend Setup Guide

## Overview
Complete frontend application for the EduTrack institutional evaluation system with real-time ML predictions, dashboards, and analytics.

## 📋 Features

### Pages
- **Landing Page** (`/`) - Welcome and introduction
- **Dashboard** (`/dashboard`) - Interactive institutional evaluation with real-time ML predictions
  - Input institution metrics via sliders
  - Real-time risk assessment
  - Performance tier prediction
  - Anomaly detection
  - Comprehensive scoring
  
- **Analytics** (`/analytics`) - Comprehensive data visualization
  - Performance distribution charts
  - Risk analysis
  - Placement trends
  - Geographic analysis
  
- **Admin Dashboard** (`/admin`) - Administrative controls
- **Institutional Dashboard** (`/institute`) - Institution-specific view
- **Review Documents** (`/reviewer`) - Document review queue
- **Upload** (`/upload`) - Document upload interface
- **Rank List** (`/rank-list`) - Institution rankings

### Components
- **MetricsCard** - Display individual metrics with color coding
- **RiskIndicator** - Visual risk level indicator with probability
- **PerformanceChart** - Interactive charts using Recharts
- **FileUploader** - Drag-and-drop file upload interface
- **Layout** - Main layout wrapper with navigation
- **Sidebar** - Navigation sidebar
- **Topbar** - Top navigation bar

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend API running at `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd c:\edutech\edutrack-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```
   
   This will install:
   - React 18.3.1
   - React Router DOM 6.30.1
   - Axios for API calls
   - Recharts for data visualization
   - Lucide React for icons
   - Tailwind CSS for styling

3. **Configure environment variables**
   
   Create `.env.local` file in the frontend root:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```
   
   Server will run at: `http://localhost:5173`

### Build for Production
```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
edutrack-frontend/
├── src/
│   ├── components/
│   │   ├── MetricsCard.jsx        # Individual metric display
│   │   ├── RiskIndicator.jsx      # Risk level visualization
│   │   ├── PerformanceChart.jsx   # Chart component
│   │   ├── Layout.jsx              # Main layout
│   │   ├── Sidebar.jsx             # Navigation sidebar
│   │   ├── Topbar.jsx              # Top navigation
│   │   └── ...
│   ├── pages/
│   │   ├── Dashboard.jsx           # ML Evaluation Dashboard
│   │   ├── Analytics.jsx           # Analytics visualizations
│   │   ├── Landing.jsx             # Landing page
│   │   ├── Login.jsx               # Login page
│   │   ├── InstitutedDashboard.jsx # Institution view
│   │   ├── AdminDashboard.jsx      # Admin controls
│   │   ├── RankList.jsx            # Rankings
│   │   ├── Upload.jsx              # Upload interface
│   │   └── ...
│   ├── contexts/
│   │   └── AuthContext.jsx         # Authentication state
│   ├── api/
│   │   ├── api.js                  # API client
│   │   └── authClient.js           # Auth client
│   ├── data/
│   │   └── dummyUsers.js           # Sample data
│   ├── App.jsx                     # Main app component
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── public/                         # Static assets
├── package.json                    # Dependencies
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # Tailwind CSS config
├── postcss.config.js               # PostCSS config
└── index.html                      # HTML template
```

## 🔌 API Integration

The frontend connects to the EduTrack backend API endpoints:

### ML Prediction Endpoints

**Get API Health**
```javascript
import { ml } from "./api/api";
const health = await ml.checkHealth();
```

**Predict Risk**
```javascript
const risk = await ml.predictRisk({
  college_name: "Sample Institute",
  total_students: 3500,
  placement_rate: 85,
  dss: 78,
  // ... other metrics
});
```

**Predict Performance**
```javascript
const performance = await ml.predictPerformance(institutionData);
```

**Detect Anomalies**
```javascript
const anomaly = await ml.detectAnomalies(institutionData);
```

**Comprehensive Evaluation**
```javascript
const comprehensive = await ml.evaluateInstitution(institutionData);
// Returns: risk_assessment, performance_prediction, anomaly_detection, comprehensive_score
```

**Batch Evaluation**
```javascript
const batchResults = await ml.batchEvaluate([institution1, institution2, ...]);
```

## 🎨 Styling

### Tailwind CSS Configuration
- Primary color: `#667eea`
- Secondary color: `#764ba2`
- Success: `#10b981`
- Warning: `#f59e0b`
- Danger: `#ef4444`

### Color Utility Classes
```jsx
// Use with Tailwind classes
<div className="bg-gradient-to-r from-primary to-secondary text-white">
  Content
</div>
```

## 📊 Dashboard Features

### Interactive Institutional Dashboard
1. **Input Panel** (Left):
   - Adjust institution metrics with sliders
   - Real-time updates
   - Field validation

2. **Results Panel** (Right):
   - Risk assessment with probability
   - Performance tier with confidence
   - Comprehensive score (0-100)
   - Anomaly detection status

### Analytics Dashboard
- **Performance Distribution**: Histogram of institution scores
- **Risk Analysis**: Risk level breakdown
- **Placement Trends**: Historical placement rate trends
- **Geographic Analysis**: State-wise performance metrics

## 🔐 Authentication

Authentication context is available in `src/contexts/AuthContext.jsx`:

```javascript
import { useAuth } from "./contexts/AuthContext";

function Component() {
  const { user, login, logout } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return <ProtectedContent />;
}
```

## 📝 Environment Variables

Create `.env.local` with:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=EduTrack
VITE_APP_VERSION=1.0.0
```

## 🐛 Troubleshooting

### API Connection Issues
- Ensure backend is running: `python -m uvicorn src.api.main:app --reload`
- Check API is accessible: `curl http://localhost:8000/health`
- Verify CORS is enabled on backend
- Check frontend environment variables

### Missing Dependencies
```bash
npm install
npm install recharts lucide-react clsx axios
```

### Port Already in Use
```bash
# Change port in vite.config.js or use:
npm run dev -- --port 3000
```

### Tailwind CSS Not Loading
```bash
# Rebuild CSS bundles
npm run build
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t edutrack-frontend .

# Run container
docker run -p 80:80 edutrack-frontend
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel deploy
```

### AWS S3 + CloudFront
```bash
# Build static files
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket/
```

## 📚 Available Scripts

```bash
npm run dev         # Start development server
npm run build       # Build for production
npm run preview     # Preview production build
```

## 🤝 Backend Integration

### Required Backend Endpoints
- `GET /health` - API health check
- `POST /predict/risk` - Risk prediction
- `POST /predict/performance` - Performance prediction
- `POST /predict/anomaly` - Anomaly detection
- `POST /evaluate/institution` - Comprehensive evaluation
- `POST /batch/evaluate` - Batch evaluation

### Request Format
```javascript
{
  college_name: "String",
  total_students: Number,
  total_faculty: Number,
  placement_rate: Number (0-100),
  average_fees: Number,
  dss: Number (0-100),
  infrastructure_quality: Number (0-100),
  student_faculty_ratio: Number,
  faculty_adequacy: Number (0-100),
  financial_efficiency: Number (0-100),
  fund_utilization: Number (0-100),
  missing_doc_count: Number,
  avg_doc_dss: Number (0-100)
}
```

## 💡 Tips

1. **API Response Caching**: Use react-query for efficient API calls
2. **State Management**: Consider Redux for complex state
3. **Performance**: Implement code splitting for large pages
4. **SEO**: Use React Helmet for meta tags
5. **Testing**: Add Jest + React Testing Library tests

## 📞 Support

For issues or questions:
1. Check backend logs: `uvicorn logs`
2. Verify API endpoints with Postman
3. Review browser console for errors
4. Check network tab for API requests

## 📄 License

MIT License - See project LICENSE file

---

**Frontend Version**: 1.0.0  
**Last Updated**: March 22, 2026
