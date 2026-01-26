# LaundryConnect Mobile App

React Native mobile application for LaundryConnect platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Expo CLI
- iOS Simulator (macOS) or Android Emulator

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run on iOS (macOS only)
npm run ios

# Run on Android
npm run android

# Run on web (for testing)
npm run web
```

## 📱 Features

- ✅ User Authentication (Login/Register)
- ✅ Home Dashboard
- ✅ Service Browsing
- ✅ Order Management
- ✅ User Profile
- ✅ Redux State Management
- ✅ JWT Token Authentication
- ✅ API Integration

## 🛠️ Tech Stack

- **Framework**: Expo (React Native)
- **Language**: TypeScript
- **State Management**: Redux Toolkit
- **Navigation**: React Navigation
- **HTTP Client**: Axios
- **Storage**: AsyncStorage

## 📁 Project Structure

```
src/
├── api/              # API client and configuration
├── constants/        # App constants and API endpoints
├── navigation/       # Navigation configuration
├── screens/          # Screen components
├── store/            # Redux store and slices
├── types/            # TypeScript type definitions
└── App.tsx          # Main app component
```

## 🔧 Configuration

Create a `.env` file in the mobile directory:

```env
API_URL=http://localhost:8000/api
WS_URL=ws://localhost:8000/ws
```

## 📡 API Endpoints

The app connects to the LaundryConnect Django backend:

- Authentication: `/api/accounts/`
- Services: `/api/services/`
- Orders: `/api/orders/`
- Mobile-specific: `/api/mobile/`

## 🧪 Testing

```bash
# Run tests (to be implemented)
npm test

# Run linter
npm run lint
```

## 📦 Building

```bash
# Create production build
expo build:android
expo build:ios
```

## 📝 Development Notes

- All screens are in `src/screens/`
- Redux slices are in `src/store/slices/`
- API configuration is in `src/constants/api.ts`
- Types are defined in `src/types/index.ts`

## 🤝 Contributing

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

Proprietary - All rights reserved

## 📞 Support

For issues or questions, contact the development team.

---

Generated with [Claude Code](https://claude.com/claude-code)
