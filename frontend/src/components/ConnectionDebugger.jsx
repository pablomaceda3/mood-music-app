import React, { useState } from 'react';

// A simple component to test API connectivity
const ConnectionDebugger = () => {
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000');

  const testConnection = async () => {
    setLoading(true);
    try {
      console.log(`Testing connection to: ${backendUrl}`);
      
      const startTime = Date.now();
      const response = await fetch(`${backendUrl}/moods`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      const endTime = Date.now();
      
      const responseTime = endTime - startTime;
      
      if (response.ok) {
        const data = await response.json();
        setTestResult({
          success: true,
          status: response.status,
          statusText: response.statusText,
          data: data,
          responseTime: `${responseTime}ms`,
        });
      } else {
        setTestResult({
          success: false,
          status: response.status,
          statusText: response.statusText,
          responseTime: `${responseTime}ms`,
        });
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      setTestResult({
        success: false,
        error: error.message || 'Unknown error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto bg-white rounded-lg shadow-md mt-10">
      <h2 className="text-2xl font-bold mb-4">Backend Connection Debugger</h2>
      
      <div className="mb-4">
        <label htmlFor="backendUrl" className="block font-medium mb-1">Backend URL:</label>
        <input
          id="backendUrl"
          type="text"
          value={backendUrl}
          onChange={(e) => setBackendUrl(e.target.value)}
          className="w-full p-2 border rounded"
        />
      </div>
      
      <button
        onClick={testConnection}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
      >
        {loading ? 'Testing...' : 'Test Connection'}
      </button>
      
      {testResult && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2">Test Results:</h3>
          <div className={`p-4 rounded ${testResult.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <p className="font-bold">
              Status: {testResult.success ? 'Success' : 'Failed'}
            </p>
            {testResult.status && (
              <p>Status Code: {testResult.status} ({testResult.statusText})</p>
            )}
            {testResult.responseTime && (
              <p>Response Time: {testResult.responseTime}</p>
            )}
            {testResult.error && (
              <p className="text-red-600">Error: {testResult.error}</p>
            )}
            {testResult.data && (
              <div className="mt-2">
                <p className="font-semibold">Data Preview:</p>
                <pre className="bg-gray-800 text-white p-2 rounded overflow-auto mt-2 text-sm">
                  {JSON.stringify(testResult.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConnectionDebugger;