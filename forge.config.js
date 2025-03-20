module.exports = {
  packagerConfig: {
    asar: true,
    icon: './images/Genie',
    extraResource: [
      './models'
    ],
    ignore: [
      /^\/\.git/,
      /^\/\.vscode/,
      /^\/docs/,
      /^\/memory-bank/,
      /^\/node_modules\/.*\.ts$/,
      /^\/src\/.*\.ts$/,
      /^\/\.env/,
      /^\/venv/,
      /^\/\.gitignore/,
      /^\/\.clinerules/,
    ],
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'genie-whisper',
        iconUrl: 'https://raw.githubusercontent.com/user/genie-whisper/main/images/Genie.png',
        setupIcon: './images/Genie.png',
      },
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['darwin'],
    },
    {
      name: '@electron-forge/maker-deb',
      config: {
        options: {
          icon: './images/Genie.png',
        },
      },
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {
        options: {
          icon: './images/Genie.png',
        },
      },
    },
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
  ],
  hooks: {
    packageAfterCopy: async (config, buildPath, electronVersion, platform, arch) => {
      // Copy Python files
      const fs = require('fs');
      const path = require('path');
      const { spawn } = require('child_process');
      
      // Create python directory
      const pythonDir = path.join(buildPath, 'python');
      if (!fs.existsSync(pythonDir)) {
        fs.mkdirSync(pythonDir);
      }
      
      // Copy Python files
      const pythonFiles = fs.readdirSync('./python');
      pythonFiles.forEach(file => {
        if (file.endsWith('.py')) {
          fs.copyFileSync(
            path.join('./python', file),
            path.join(pythonDir, file)
          );
        }
      });
      
      // Create scripts directory
      const scriptsDir = path.join(buildPath, 'scripts');
      if (!fs.existsSync(scriptsDir)) {
        fs.mkdirSync(scriptsDir);
      }
      
      // Copy script files
      const scriptFiles = fs.readdirSync('./scripts');
      scriptFiles.forEach(file => {
        if (file.endsWith('.py')) {
          fs.copyFileSync(
            path.join('./scripts', file),
            path.join(scriptsDir, file)
          );
        }
      });
      
      // Create models directory if it doesn't exist
      const modelsDir = path.join(buildPath, 'models');
      if (!fs.existsSync(modelsDir)) {
        fs.mkdirSync(modelsDir);
      }
      
      // Copy models README
      fs.copyFileSync(
        path.join('./models', 'README.md'),
        path.join(modelsDir, 'README.md')
      );
      
      console.log('Additional files copied successfully');
    },
    packageAfterPrune: async (config, buildPath, electronVersion, platform, arch) => {
      // Install Python dependencies in the packaged app
      const { spawn } = require('child_process');
      const path = require('path');
      
      // Copy requirements.txt
      const fs = require('fs');
      fs.copyFileSync(
        path.join('.', 'requirements.txt'),
        path.join(buildPath, 'requirements.txt')
      );
      
      console.log('Installing Python dependencies...');
      
      // Use pip to install dependencies
      return new Promise((resolve, reject) => {
        const pip = spawn(
          'pip',
          [
            'install',
            '-r',
            'requirements.txt',
            '--target',
            path.join(buildPath, 'python_modules'),
            '--upgrade'
          ],
          { cwd: buildPath, stdio: 'inherit' }
        );
        
        pip.on('close', (code) => {
          if (code === 0) {
            console.log('Python dependencies installed successfully');
            resolve();
          } else {
            console.error(`Python dependencies installation failed with code ${code}`);
            reject(new Error(`Python dependencies installation failed with code ${code}`));
          }
        });
      });
    },
  },
};