# Mobile App Web Setup & Troubleshooting

## Overview
The LaundryConnect mobile app is built with React Native and Expo, supporting iOS, Android, and Web platforms.

## Recent Fixes Applied

### 1. Android Package Configuration
**Issue:** `CommandError: Required property 'android.package' is not found`

**Fix:** Added package identifiers to `app.json`:
```json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.laundryconnect.mobile"
    },
    "android": {
      "package": "com.laundryconnect.mobile"
    }
  }
}
```

### 2. Web Blank Screen Issue
**Issue:** Web version shows blank screen

**Fixes Applied:**
1. **Error Boundary** - Added `ErrorBoundary.tsx` to catch and display errors
2. **Platform-specific Loading** - Added proper loading indicators for web
3. **Console Logging** - Added debug logs to track app initialization
4. **SafeAreaProvider** - Wrapped app in SafeAreaProvider for proper layout
5. **Web Entry Point** - Created `index.web.js` for web-specific initialization

## Running the Mobile App

### For All Platforms
```bash
cd mobile
npx expo start
```

Then choose your platform:
- Press `w` to open in **web browser**
- Press `a` to open in **Android emulator**
- Press `i` to open in **iOS simulator**

### Web-Specific
```bash
cd mobile
npx expo start --web
```

This will automatically open the app in your default web browser at `http://localhost:8081` (or another port if 8081 is busy).

## Troubleshooting Web Issues

### Blank Screen on Web

If you see a blank screen when opening the web version, check the following:

#### 1. Check Browser Console
Open browser DevTools (F12) and look for:
- Console logs showing app initialization
- Any error messages (red text)
- Network errors (failed to load resources)

You should see:
```
App component rendering...
Platform: web
Checking authentication...
Token exists: false
Auth check complete
```

#### 2. Common Issues & Solutions

**Issue: `AsyncStorage is not available`**
- **Solution:** Already fixed - AsyncStorage should work with proper Expo setup
- If still failing, check that `@react-native-async-storage/async-storage` is installed

**Issue: Navigation container errors**
- **Solution:** Check that `@react-navigation/*` packages are installed
- Clear cache: `npx expo start --clear`

**Issue: Redux store errors**
- **Solution:** Check browser console for specific Redux errors
- Verify API endpoint is accessible from browser

**Issue: Network requests failing**
- **Solution:** Update API base URL in `src/api/client.ts`
- For local development, use: `http://localhost:8000/api/`
- For web, ensure CORS is enabled on Django backend

#### 3. Clear Cache and Restart
```bash
cd mobile
# Clear Expo cache
npx expo start --clear

# Or clear npm cache
rm -rf node_modules
npm install
npx expo start
```

#### 4. Check Dependencies
Ensure all required packages are installed:
```bash
cd mobile
npm install
```

Key dependencies:
- `expo` - Core Expo framework
- `react-native-web` - React Native for web
- `@react-navigation/*` - Navigation
- `@reduxjs/toolkit` - State management
- `@react-native-async-storage/async-storage` - Storage

## Backend Configuration for Web

### CORS Settings
For the web app to communicate with Django backend, ensure CORS is properly configured:

In `config/settings/development.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # For development only!
CORS_ALLOW_CREDENTIALS = True

# Or for production, specify allowed origins:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8081",
#     "http://127.0.0.1:8081",
# ]
```

### API Base URL
The mobile app's API client should point to your Django backend.

Check `mobile/src/api/client.ts`:
```typescript
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/';
```

For web development, you can set the environment variable:
```bash
# In mobile/.env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/
```

## Debugging Steps

### Step 1: Verify App Loads
1. Open web app in browser
2. Open browser DevTools (F12)
3. Check Console tab for:
   - "App component rendering..." ✓
   - "Platform: web" ✓
   - No red errors ✓

### Step 2: Verify Navigation Works
1. App should show Login screen initially (if not authenticated)
2. Try navigating to Register screen
3. Check that UI elements are clickable

### Step 3: Verify API Communication
1. Try to login with demo credentials
2. Check Network tab in DevTools
3. Look for API requests to Django backend
4. Check response status codes

### Step 4: Check Error Boundary
If you see the error boundary screen:
1. Note the error message displayed
2. Check browser console for full error details
3. Click "Try Again" to attempt recovery

## Console Debug Output

When the app loads correctly, you should see this sequence in browser console:

```
App component rendering...
Platform: web
Checking authentication...
Token exists: false
Auth check complete
```

If authentication token is found:
```
Platform: web
Checking authentication...
Token exists: true
[API request logs...]
Auth check complete
```

## Development Tips

### Hot Reload
Expo supports hot reloading. Changes to code should automatically refresh the web app.

### Environment Variables
Create `mobile/.env` for environment-specific configuration:
```
EXPO_PUBLIC_API_URL=http://localhost:8000/api/
EXPO_PUBLIC_APP_NAME=LaundryConnect
```

### Testing Web-Specific Features
Some features may need web-specific handling:
- File uploads
- Camera access
- Geolocation
- Push notifications (not available on web)

## Production Build

To create a production web build:
```bash
cd mobile
npx expo export --platform web
```

Output will be in `mobile/dist/` directory, ready to deploy to a web server.

## Known Limitations on Web

- No native mobile features (camera, push notifications)
- Some React Native components may have limited styling on web
- Performance may vary compared to native apps
- AsyncStorage uses browser localStorage

## Support & Resources

- **Expo Docs:** https://docs.expo.dev/
- **React Navigation:** https://reactnavigation.org/
- **React Native Web:** https://necolas.github.io/react-native-web/

## Quick Reference

| Command | Description |
|---------|-------------|
| `npx expo start` | Start development server |
| `npx expo start --web` | Start web only |
| `npx expo start --clear` | Clear cache and start |
| `npm install` | Install dependencies |
| `npx expo doctor` | Check for issues |

---

**Last Updated:** 2026-01-06
**Platform:** Web, iOS, Android
**Framework:** React Native + Expo
