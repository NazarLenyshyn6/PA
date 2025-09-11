'use client';

import React, { useState } from 'react';
import { Upload, MessageSquare, FileText, LogOut } from 'lucide-react';

const DashboardPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('file_name', selectedFile.name);
    formData.append('session_id', '00000000-0000-0000-0000-000000000000'); // Default session ID for dashboard uploads

    try {
      const response = await fetch('http://localhost:8000/api/v1/files', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        console.log('File uploaded successfully');
        alert('File uploaded successfully!');
        setSelectedFile(null);
      } else {
        console.error('File upload failed');
        alert('File upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload error. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleLogout = () => {
    // Clear any stored auth tokens and redirect to login
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-green-800 rounded-full flex items-center justify-center mr-3">
                <span className="text-white font-bold text-sm">A4E</span>
              </div>
              <span className="text-xl font-semibold text-gray-800">Agents4Energy Dashboard</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to Agents4Energy</h1>
          <p className="text-gray-600">Upload your energy data and interact with specialized AI agents</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* File Upload Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <Upload className="mr-2" size={24} />
                Upload Energy Data
              </h2>
              
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileSelect}
                    accept=".csv,.json,.xlsx,.txt"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                    <p className="text-gray-600">Upload energy datasets, production data, and field reports</p>
                    <p className="text-sm text-gray-500 mt-1">CSV, JSON, XLSX, TXT files</p>
                  </label>
                </div>

                {selectedFile && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-800">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                  </div>
                )}

                <button
                  onClick={handleFileUpload}
                  disabled={!selectedFile || isUploading}
                  className="w-full bg-green-800 text-white py-3 rounded-lg font-medium hover:bg-green-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Uploading...' : 'Upload File'}
                </button>
              </div>
            </div>

            {/* Recent Files */}
            <div className="bg-white rounded-xl shadow-sm border p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <FileText className="mr-2" size={20} />
                Recent Files
              </h3>
              <div className="space-y-2">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-800">data_analysis.csv</p>
                  <p className="text-xs text-gray-500">Uploaded 2 hours ago</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-800">customer_data.json</p>
                  <p className="text-xs text-gray-500">Uploaded yesterday</p>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border h-96 flex flex-col">
              <div className="p-4 border-b flex items-center">
                <MessageSquare className="mr-2" size={24} />
                <h2 className="text-xl font-semibold text-gray-800">Chat with Energy Agent</h2>
              </div>

              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-4">
                  <div className="flex">
                    <div className="bg-gray-100 rounded-lg p-3 max-w-xs">
                      <p className="text-sm text-gray-800">Hello! I&apos;m your Energy Agent. Upload energy data and ask me to analyze reservoir performance, production optimization, or field operations.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Ask me about your energy data..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-800 focus:border-transparent"
                  />
                  <button className="bg-green-800 text-white px-6 py-2 rounded-lg hover:bg-green-900 transition-colors">
                    Send
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="bg-green-50 border border-green-200 rounded-lg p-4 text-left hover:bg-green-100 transition-colors">
                <h3 className="font-semibold text-green-800 mb-1">Reservoir Analysis</h3>
                <p className="text-sm text-green-600">Analyze reservoir characteristics and performance</p>
              </button>
              <button className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-left hover:bg-orange-100 transition-colors">
                <h3 className="font-semibold text-orange-800 mb-1">Production Optimization</h3>
                <p className="text-sm text-orange-600">Optimize well performance and production</p>
              </button>
              <button className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-left hover:bg-amber-100 transition-colors">
                <h3 className="font-semibold text-amber-800 mb-1">Asset Integrity</h3>
                <p className="text-sm text-amber-600">Monitor and assess asset integrity</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;