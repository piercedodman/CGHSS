'use client';

import React, { useState, useEffect } from 'react';

export default function Home() {
  const [agencies, setAgencies] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedAgency, setSelectedAgency] = useState('');
  const [selectedEvent, setSelectedEvent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [flowchartUrl, setFlowchartUrl] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    // When component mounts, fetch the available agencies and events
    const fetchOptions = async () => {
      try {
        const response = await fetch('http://localhost:8000/get-options');
        const data = await response.json();
        setAgencies(data.agencies);
        setEvents(data.events);
      } catch (error) {
        console.error('Failed to fetch options:', error);
        setError('Failed to load available options. Please try again later.');
      }
    };

    fetchOptions();
  }, []);

  interface AgencyEventOptions {
    agencies: string[];
    events: string[];
  }

  interface FlowchartResponse {
    blob: Blob;
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedAgency || !selectedEvent) {
      setError('Please select both an agency and an event');
      return;
    }

    setIsLoading(true);
    setError('');
    setFlowchartUrl(null);

    const formData = new FormData();
    formData.append('agency', selectedAgency);
    formData.append('event', selectedEvent);

    try {
      const response = await fetch('http://localhost:8000/generate-flowchart', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setFlowchartUrl(url);
    } catch (error: any) {
      console.error('Error:', error);
      setError(error.message || 'Error generating flowchart');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Emergency Powers Flowchart Generator
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="mb-4">
              <h2 className="text-2xl font-semibold text-gray-700 mb-6">Generate Flowchart</h2>
            </div>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="agency" className="block text-sm font-medium text-gray-700 mb-2">
                  Agency
                </label>
                <select
                  id="agency"
                  value={selectedAgency}
                  onChange={(e) => setSelectedAgency(e.target.value)}
                  className="w-full rounded-md border border-gray-300 text-gray-700 shadow-sm p-2"
                >
                  <option value="">Select an agency</option>
                  {agencies.map((agency) => (
                    <option key={agency} value={agency}>
                      {agency}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="event" className="block text-sm font-medium text-gray-700 mb-2">
                  Triggering Event
                </label>
                <select
                  id="event"
                  value={selectedEvent}
                  onChange={(e) => setSelectedEvent(e.target.value)}
                  className="w-full rounded-md border border-gray-300 text-gray-700 shadow-sm p-2"
                >
                  <option value="">Select an event</option>
                  {events.map((event) => (
                    <option key={event} value={event}>
                      {event}
                    </option>
                  ))}
                </select>
              </div>
              
              <button 
                type="submit" 
                disabled={isLoading || !selectedAgency || !selectedEvent}
                className={`w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors
                  ${(isLoading || !selectedAgency || !selectedEvent) ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {isLoading ? 'Generating...' : 'Generate Flowchart'}
              </button>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-600">
                  {error}
                </div>
              )}
            </form>
          </div>

          {/* Preview Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="mb-4">
              <h2 className="text-2xl font-semibold text-gray-700 mb-6">Preview</h2>
            </div>
            <div className="min-h-[400px]">
              {flowchartUrl ? (
                <img 
                  src={flowchartUrl} 
                  alt="Generated Flowchart"
                  className="w-full rounded-lg border border-gray-200"
                />
              ) : (
                <div className="h-96 flex items-center justify-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
                  {isLoading ? (
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
                      <p>Generating flowchart...</p>
                    </div>
                  ) : (
                    <p>Select an agency and event to generate a flowchart</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}