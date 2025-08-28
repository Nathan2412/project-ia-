const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // Configuration pour la production
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  outputDir: 'dist',
  
  devServer: {
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_URL || 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    }
  },
  
  // Configuration pour les variables d'environnement
  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      Object.assign(definitions[0]['process.env'], {
        VUE_APP_API_URL: JSON.stringify(process.env.VUE_APP_API_URL || 'http://localhost:5000/api')
      });
      return definitions;
    });
  }
})
