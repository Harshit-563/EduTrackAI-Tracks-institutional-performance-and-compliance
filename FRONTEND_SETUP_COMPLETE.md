# EduTrack Complete Setup & Integration Guide

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   EduTrack System                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend (React + Vite)          Backend (FastAPI)   │
│  ├─ Dashboard                     ├─ ML Models       │
│  ├─ Analytics                     │  ├─ Risk Model   │
│  ├─ Institutional View            │  ├─ Performance  │
│  └─ Admin Panel                   │  └─ Anomaly      │
│         ↓                          ├─ Data Pipeline  │
│   http://localhost:5173          │  └─ Reports     │
│         ↔~~~~~~~~~~~~API Calls~~~~~~~~~~~~~~~~~~~→    │
│                      http://localhost:8000       │
│                                                   │
│  ✓ Real-time Predictions                            │
│  ✓ Interactive Dashboards                           │
│  ✓ Comprehensive Analytics                          │
│  ✓ Batch Processing                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📦 Complete Feature Set

### Frontend Features
✅ **Dashboard**
- Interactive institutional metrics input
- Real-time ML predictions
- Risk level indicators
- Performance tier classification
- Anomaly detection

✅ **Analytics**
- Performance distribution charts
- Risk analysis visualizations
- Placement trend tracking
- Geographic analysis
- Export to PNG

✅ **Components**
- Reusable metric cards
- Risk indicators with probability
- Performance charts using Recharts
- Responsive design with Tailwind CSS

✅ **Integration**
- Axios-based API client
- Automatic error handling
- Health check status
- CORS support

### Backend Features (Already Running)
✅ **ML Models**
- Risk Classification (ROC-AUC: 1.0)
- Performance Tier Prediction (Accuracy: 95.45%)
- Anomaly Detection (242 anomalies detected)

✅ **API Endpoints**
- 7+ REST endpoints
- Real-time predictions
- Batch processing
- Health monitoring

## 🚀 Quick Start (5 minutes)

### Step 1: Verify Backend is Running ✓
```bash
# Backend should already be running
curl http://localhost:8000/health
# Expected response: {"status":"healthy","ml_models_available":true}
```

### Step 2: Install Frontend Dependencies
```bash
cd c:\edutech\edutrack-frontend
npm install
```

**Packages installed:**
- react & react-dom (18.3.1)
- react-router-dom (6.30.1)
- axios (1.6.2)
- recharts (2.10.3)
- lucide-react (0.294.0)
- tailwindcss (3.4.1)

### Step 3: Start Frontend Development Server
```bash
npm run dev
```

**Output should show:**
```
  VITE v5.4.19  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Step 4: Access the Application
Open browser and navigate to:
- **Main Dashboard**: http://localhost:5173/dashboard
- **Analytics**: http://localhost:5173/analytics
- **Landing Page**: http://localhost:5173/

## 📋 Available Pages & Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | Landing | Welcome page |
| `/dashboard` | Dashboard | Interactive ML predictions |
| `/analytics` | Analytics | Comprehensive visualizations |
| `/login` | Login | Authentication |
| `/institute` | InstituteDashboard | Institution view |
| `/admin` | AdminDashboard | Admin controls |
| `/rank-list` | RankList | Institution rankings |
| `/upload` | Upload | Document upload |
| `/reviewer` | ReviewerQueue | Document review |

## 🔌 Testing API Integration

### Test 1: Check Backend Health
```bash
curl http://localhost:8000/health
```

### Test 2: Test Risk Prediction
```bash
curl -X POST http://localhost:8000/predict/risk \
  -H "Content-Type: application/json" \
  -d '{
    "college_name": "Test Institute",
    "total_students": 3500,
    "placement_rate": 85,
    "dss": 78,
    "infrastructure_quality": 85,
    "faculty_adequacy": 92,
    "student_faculty_ratio": 14,
    "financial_efficiency": 75,
    "fund_utilization": 82,
    "total_faculty": 250,
    "missing_doc_count": 2,
    "average_fees": 450000,
    "avg_doc_dss": 78
  }'
```

### Test 3: Test Comprehensive Evaluation
```bash
curl -X POST http://localhost:8000/evaluate/institution \
  -H "Content-Type: application/json" \
  -d '{...institution_data...}'
```

## 📊 Frontend Dashboard Walkthrough

### Institutional Evaluation Dashboard (`/dashboard`)

1. **Input Panel (Left Side)**
   - Slider controls for key metrics
   - Real-time value updates
   - Metrics include:
     - Total Students (100-10,000)
     - Total Faculty (10-1,000)
     - Placement Rate (0-100%)
     - DSS Score (0-100)
     - Infrastructure Quality (0-100%)
     - Financial Efficiency (0-100%)

2. **Results Panel (Right Side)**
   - Risk Assessment: Level, probability, confidence
   - Performance Prediction: Tier and confidence score
   - Overall Score: Comprehensive rating
   - Anomaly Detection: Normal/Anomalous status

3. **Try This**
   - Adjust sliders to different values
   - Click "Evaluate Institution"
   - See ML predictions update in real-time

### Analytics Dashboard (`/analytics`)

1. **Dashboard Selector**
   - Performance Distribution
   - Risk Analysis
   - Placement Trends
   - Geographic Analysis

2. **Visualizations**
   - Interactive charts with hover tooltips
   - Export to PNG button
   - Key insights panel

3. **Statistics Summary**
   - Total Institutions: 4,831
   - States Covered: 35
   - Average Placement: 60.6%
   - High Risk: 22.1%

## 🛠️ Customization Guide

### Add New Metric to Dashboard
1. Edit `src/pages/Dashboard.jsx`
2. Add to `institutionData` state:
   ```javascript
   new_metric: 50
   ```
3. Add input slider:
   ```jsx
   <div>
     <label>New Metric: {institutionData.new_metric}</label>
     <input
       type="range"
       name="new_metric"
       value={institutionData.new_metric}
       onChange={handleInputChange}
     />
   </div>
   ```

### Modify Colors/Theme
Edit `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: "#YOUR_COLOR",
      secondary: "#YOUR_COLOR",
    },
  },
}
```

### Add New Chart
1. Create component in `src/components/`
2. Import Recharts:
   ```javascript
   import { BarChart, Bar, ... } from 'recharts'
   ```
3. Import in page and use

## 🔒 Authentication (Optional)

The app includes auth context in `src/contexts/AuthContext.jsx`:

```javascript
import { useAuth } from "./contexts/AuthContext";

function Protected() {
  const { user, login, logout } = useAuth();
  
  return user ? <Content /> : <Navigate to="/login" />;
}
```

## ⚡ Performance Tips

1. **Lazy Load Pages**
   ```javascript
   const Dashboard = lazy(() => import('./pages/Dashboard'));
   ```

2. **Memoize Components**
   ```javascript
   export default memo(MetricsCard);
   ```

3. **Use React Query for Caching**
   ```bash
   npm install @tanstack/react-query
   ```

## 🐛 Debugging

### Enable Browser DevTools
```javascript
// In main.jsx during development
if (import.meta.env.DEV) {
  console.log("Development mode active");
}
```

### Check API Calls
1. Open DevTools (F12)
2. Go to Network tab
3. Look for API requests to `localhost:8000`
4. Check response status and data

### Common Issues

| Issue | Solution |
|-------|----------|
| API not connecting | Verify backend running on :8000 |
| Styles not loading | Run `npm install` and rebuild |
| Charts not rendering | Check recharts installation |
| CORS errors | Backend CORS middleware enabled |

## 📈 Production Deployment

### Build for Production
```bash
npm run build
# Creates optimized dist/ folder
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel deploy
```

### Deploy to AWS S3
```bash
# Build static files
npm run build

# Upload to S3 bucket
aws s3 sync dist/ s3://your-bucket/

# Invalidate CloudFront cache (if using)
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `src/App.jsx` | Main routing configuration |
| `src/pages/Dashboard.jsx` | ML evaluation dashboard |
| `src/pages/Analytics.jsx` | Analytics visualizations |
| `src/api/api.js` | API client and ML endpoints |
| `src/components/MetricsCard.jsx` | Reusable metric display |
| `src/components/RiskIndicator.jsx` | Risk level visualization |
| `tailwind.config.js` | Styling configuration |

## ✅ Verification Checklist

- [ ] Backend running at `http://localhost:8000`
- [ ] Health check passes: `curl localhost:8000/health`
- [ ] Frontend dependencies installed: `npm install`
- [ ] Frontend running at `http://localhost:5173`
- [ ] Dashboard page loads without errors
- [ ] Dashboard can fetch predictions
- [ ] Analytics page displays charts
- [ ] Sliders update values in real-time
- [ ] Export button works
- [ ] No CORS errors in console

## 🎓 Learning Resources

- **Vite Documentation**: https://vitejs.dev/
- **React Documentation**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **Recharts**: https://recharts.org/

## 🚀 Next Steps

1. **Test the Dashboard**
   - Open `/dashboard`
   - Adjust institution metrics
   - Click "Evaluate Institution"
   - Observe ML predictions

2. **Explore Analytics**
   - Open `/analytics`
   - Switch between chart types
   - Download visualizations

3. **Customize Your Usage**
   - Modify color schemes
   - Add additional metrics
   - Integrate with your systems

## 📞 Support Checklist

If something doesn't work:
1. ✓ Backend running? (`uvicorn src.api.main:app --reload`)
2. ✓ Dependencies installed? (`npm install`)
3. ✓ Correct ports? (5173 for frontend, 8000 for backend)
4. ✓ Network connectivity? (CORS enabled on backend)
5. ✓ Browser console errors? (Check DevTools F12)

---

**Setup Complete!** 🎉

Your EduTrack frontend is ready to interact with the ML-powered backend.
Start exploring institutional evaluation with AI-powered predictions!

**Frontend**: http://localhost:5173  
**Backend API**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

