/**
 * Test script for Python-Electron communication
 * 
 * This script tests the communication between Electron and Python
 * by spawning the Python server and verifying that:
 * 1. JSON messages are correctly received from stdout
 * 2. Logs are correctly received from stderr
 * 3. Commands can be sent to the Python process
 */

const { spawn } = require('child_process');
const path = require('path');

// Configuration
const pythonPath = 'python';
const scriptPath = path.resolve(__dirname, 'python', 'server.py');
const args = [
  '-u',  // Unbuffered output
  '--model-size', 'base',
  '--sensitivity', '0.5',
  '--vad', 'true',
  '--offline', 'true',
  '--activation-mode', 'manual'
];

console.log('Starting Python server...');
console.log(`Command: ${pythonPath} ${scriptPath} ${args.join(' ')}`);

// Spawn Python process
const pythonProcess = spawn(pythonPath, [scriptPath, ...args], {
  stdio: ['pipe', 'pipe', 'pipe']
});

// Handle stdout (JSON messages)
pythonProcess.stdout.on('data', (data) => {
  const lines = data.toString().trim().split('\n').filter(Boolean);
  
  lines.forEach(line => {
    try {
      // Parse message as JSON
      const jsonData = JSON.parse(line);
      console.log('✅ Received JSON message:', jsonData);
    } catch (error) {
      console.error('❌ Invalid JSON from Python stdout:', line);
    }
  });
});

// Handle stderr (logs)
pythonProcess.stderr.on('data', (data) => {
  console.log('📋 Python stderr:', data.toString().trim());
});

// Handle process errors
pythonProcess.on('error', (err) => {
  console.error('❌ Python Process Error:', err);
});

// Handle process exit
pythonProcess.on('close', (code) => {
  console.log(`Python process closed with code ${code}`);
});

// Send a test command after 5 seconds
setTimeout(() => {
  console.log('Sending test command...');
  const command = JSON.stringify({ type: 'get_devices' });
  pythonProcess.stdin.write(command + '\n');
}, 5000);

// Kill the process after 10 seconds
setTimeout(() => {
  console.log('Test complete, killing Python process...');
  pythonProcess.kill();
}, 10000);
