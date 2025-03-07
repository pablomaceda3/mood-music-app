import { useState } from 'react'
import MoodTransition from './components/MoodTransition'
import ConnectionDebugger from './components/ConnectionDebugger'

function App() {
  const [showDebugger, setShowDebugger] = useState(false);

  return (
    <div className="w-full">
      <button 
        onClick={() => setShowDebugger(!showDebugger)}
        className="fixed top-4 right-4 bg-gray-200 px-3 py-1 rounded-md text-sm z-50"
      >
        {showDebugger ? 'Hide Debugger' : 'Debug Connection'}
      </button>
      
      {showDebugger && <ConnectionDebugger />}
      <MoodTransition />
    </div>
  )
}

export default App