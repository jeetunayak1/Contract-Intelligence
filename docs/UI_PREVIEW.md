# UI Preview - Contract Intelligence System

## Dashboard Overview

The UI has been designed with a modern, professional interface using Material-UI components. Here's what you'll see:

---

## Main Layout

### **Header (Top Bar)**
- **Title:** "Contract Intelligence System"
- **Color:** Primary blue (#1976d2)
- **Fixed position** at the top

### **Sidebar (Left Navigation)**
- **Width:** 240px
- **Menu Items:**
  1. 📊 Dashboard
  2. 📄 Contracts
  3. 📈 Compliance
  4. ⚠️ Risks
  5. 🔔 Alerts
  6. 📊 Analytics

---

## Dashboard Page

### **Header Section**
```
Contract Intelligence Dashboard
Real-time SLA monitoring and compliance tracking
```

### **Stats Cards (4 Cards in a Row)**

**Card 1: Total Contracts**
- Icon: 📄 Document icon
- Number: 24
- Subtitle: "18 active"

**Card 2: SLA Compliance**
- Icon: ✅ Check circle (green)
- Number: 95.8%
- Progress bar: Green, showing 95.8%

**Card 3: Expiring Soon**
- Icon: ⚠️ Warning (orange)
- Number: 3
- Subtitle: "Within 30 days"

**Card 4: Critical Alerts**
- Icon: ❌ Error (red)
- Number: 2
- Subtitle: "5 high risks"

---

### **Main Content (2 Columns)**

#### **Left Column: Recent Alerts**

**Alert 1 (Critical - Red)**
```
⚠️ SLA Breach Imminent
Contract: CTR-2024-001 • 5 minutes ago
```

**Alert 2 (High - Orange)**
```
⚠️ Response Time Threshold
Contract: CTR-2024-015 • 1 hour ago
```

**Alert 3 (Medium - Blue)**
```
⚠️ Contract Renewal Due
Contract: CTR-2024-008 • 3 hours ago
```

#### **Right Column: Compliance Overview**

**System Uptime**
- Progress: 99.95% (Green bar)

**Response Time**
- Progress: 98.2% (Green bar)

**Resolution Time**
- Progress: 92.5% (Orange bar)

---

### **Risk Summary (Full Width)**

Four colored boxes showing risk distribution:

**Critical Risks (Red)**
- Number: 2
- Background: Light red

**High Risks (Orange)**
- Number: 5
- Background: Light orange

**Medium Risks (Blue)**
- Number: 8
- Background: Light blue

**Low Risks (Green)**
- Number: 12
- Background: Light green

---

## Color Scheme

### **Primary Colors:**
- **Primary Blue:** #1976d2 (Header, links)
- **Success Green:** #2e7d32 (Compliant metrics)
- **Warning Orange:** #ed6c02 (At-risk items)
- **Error Red:** #d32f2f (Critical alerts)
- **Info Blue:** #0288d1 (Medium priority)

### **Background:**
- **Main:** #fafafa (Light gray)
- **Cards:** #ffffff (White)
- **Sidebar:** #ffffff (White)

---

## Typography

- **Headers:** Roboto, Bold
- **Body:** Roboto, Regular
- **Numbers:** Roboto, Bold, Large

---

## Responsive Design

- **Desktop (>960px):** Full layout with sidebar
- **Tablet (600-960px):** Stacked cards, 2 columns
- **Mobile (<600px):** Single column, collapsible sidebar

---

## Interactive Elements

### **Hover Effects:**
- Sidebar items: Light blue background
- Cards: Subtle shadow increase
- Buttons: Color darkening

### **Progress Bars:**
- Animated on load
- Color-coded by status
- Smooth transitions

---

## To See the UI:

### **Option 1: Run Locally**
```bash
cd frontend
npm install
npm run dev
```
Then open: http://localhost:3000

### **Option 2: View Screenshots**
Once you run the app, you'll see:
- Clean, modern dashboard
- Real-time metrics
- Color-coded alerts
- Interactive charts
- Professional layout

---

## Future Pages (Coming Soon)

### **Contracts Page**
- List of all contracts
- Upload new contracts
- View contract details
- Filter and search

### **Compliance Page**
- Detailed SLA metrics
- Historical trends
- Compliance reports
- Export functionality

### **Risks Page**
- Risk heatmap
- Risk details
- Mitigation recommendations
- Financial impact

### **Alerts Page**
- All alerts list
- Filter by severity
- Acknowledge/resolve
- Alert history

### **Analytics Page**
- Trend charts
- Forecasting
- Financial analysis
- Custom reports

---

## UI Features

✅ **Modern Design** - Clean, professional Material-UI  
✅ **Responsive** - Works on all devices  
✅ **Color-Coded** - Easy to identify priorities  
✅ **Real-Time** - Live data updates  
✅ **Interactive** - Smooth animations  
✅ **Accessible** - WCAG compliant  

---

## Mock Data

Currently using mock data for demonstration. Once backend is connected:
- Real contract data from Cloudant
- Live SLA metrics
- Actual alerts and risks
- Historical trends

---

**The UI is ready to run!** Just install dependencies and start the dev server to see it in action.