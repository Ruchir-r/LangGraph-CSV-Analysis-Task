// Quick test to verify APIService import fix
import APIService from './services/api';

console.log('Testing APIService import...');

try {
  const apiService = new APIService();
  console.log('✅ APIService constructor works!');
  console.log('APIService instance:', apiService);
} catch (error) {
  console.error('❌ APIService constructor failed:', error);
}

export default APIService;