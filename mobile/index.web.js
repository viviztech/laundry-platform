/**
 * Web-specific entry point for React Native Web
 */
import { AppRegistry } from 'react-native';
import App from './App';

// Register the app for web
AppRegistry.registerComponent('main', () => App);

// Run the app
AppRegistry.runApplication('main', {
  rootTag: document.getElementById('root'),
});
