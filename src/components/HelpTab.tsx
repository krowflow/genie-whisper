import React from 'react';

const HelpTab: React.FC = () => {
  return (
    <div className="flex-grow p-4 overflow-y-auto">
      <h2 className="text-lg font-medium text-white mb-4">Genie Whisper Help</h2>
      
      <div className="space-y-6">
        <section>
          <h3 className="text-md font-medium text-cyan-300 mb-2">Getting Started</h3>
          <p className="text-gray-300 mb-2">
            Genie Whisper is a real-time voice-to-text transcription tool designed to work offline and online, 
            integrating seamlessly with Cursor, VS Code, Roo Code, and Cline Dev.
          </p>
          <p className="text-gray-300">
            To start transcribing, simply click the microphone button or press the configured hotkey 
            (default: Ctrl+Shift+Space).
          </p>
        </section>
        
        <section>
          <h3 className="text-md font-medium text-cyan-300 mb-2">Activation Methods</h3>
          <ul className="list-disc pl-5 text-gray-300 space-y-1">
            <li><strong>Manual Activation</strong>: Click the microphone button or use the hotkey.</li>
            <li><strong>Wake Word</strong>: Say "Hey Genie" to activate hands-free (if enabled in settings).</li>
            <li><strong>Always On</strong>: Continuous transcription (if enabled in settings).</li>
          </ul>
        </section>
        
        <section>
          <h3 className="text-md font-medium text-cyan-300 mb-2">Keyboard Shortcuts</h3>
          <div className="bg-indigo-900 bg-opacity-50 rounded p-3">
            <table className="w-full text-gray-300">
              <tbody>
                <tr>
                  <td className="py-1 pr-4 font-medium">Ctrl+Shift+Space</td>
                  <td>Start/Stop Listening</td>
                </tr>
                <tr>
                  <td className="py-1 pr-4 font-medium">Ctrl+,</td>
                  <td>Open Settings</td>
                </tr>
                <tr>
                  <td className="py-1 pr-4 font-medium">Ctrl+H</td>
                  <td>Open Help</td>
                </tr>
                <tr>
                  <td className="py-1 pr-4 font-medium">Ctrl+D</td>
                  <td>Open Devices</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
        
        <section>
          <h3 className="text-md font-medium text-cyan-300 mb-2">Troubleshooting</h3>
          <div className="space-y-2">
            <div>
              <h4 className="text-sm font-medium text-white">No audio input detected</h4>
              <p className="text-gray-400">
                Make sure your microphone is connected and selected in the Devices tab.
                Check system permissions for microphone access.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">Transcription is inaccurate</h4>
              <p className="text-gray-400">
                Try adjusting the sensitivity in Settings, or select a larger model size for better accuracy.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-white">High CPU usage</h4>
              <p className="text-gray-400">
                Select a smaller model size or enable GPU acceleration if available.
              </p>
            </div>
          </div>
        </section>
        
        <section>
          <h3 className="text-md font-medium text-cyan-300 mb-2">About</h3>
          <p className="text-gray-300">
            Genie Whisper v0.1.0<br />
            Using OpenAI Whisper for transcription<br />
            © 2025 Genie Whisper Team
          </p>
        </section>
      </div>
    </div>
  );
};

export default HelpTab;