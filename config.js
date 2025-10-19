// Configuration for PokéInfo application

const CONFIG = {
  // API Configuration
  API: {
    // Auto-detect environment
    getBaseUrl: function() {
      // Development environment (localhost)
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8080';
      }
      // Production environment - use relative URL
      return '';
    },
    
    // API endpoints
    endpoints: {
      pokemonInfo: '/info/{name}',
      healthCheck: '/alive/'
    }
  },
  
  // UI Configuration
  UI: {
    loaderAnimationDuration: 1500, // ms
    animationDelay: 200, // ms
    typeEffectOpacity: 0.3
  },
  
  // Caching Configuration
  CACHE: {
    enabled: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours in milliseconds
  }
};