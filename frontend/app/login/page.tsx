'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff } from 'lucide-react';

interface LoginFormData {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8003/api/v1/gateway/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Store the access token
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type);
        // Mark as new login to trigger session creation
        localStorage.setItem('isNewLogin', 'true');
        console.log('Login successful');
        // Redirect to chat - the chat page will automatically create and load the new session
        router.push('/chat');
      } else {
        // Handle login error
        console.error('Login failed');
        alert('Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl border-2 border-blue-100 overflow-hidden max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2">
        {/* Left Side - Login Form */}
        <div className="p-12 flex flex-col justify-center">
          <div className="max-w-md w-full mx-auto">

            {/* Welcome Text */}
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome Back!</h1>
            <p className="text-gray-600 mb-8">Please enter log in details below</p>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <input
                  type="email"
                  name="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-4 bg-blue-50 border-2 border-blue-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 transition-all shadow-sm hover:shadow-md"
                />
              </div>

              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-4 bg-blue-50 border-2 border-blue-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 transition-all shadow-sm hover:shadow-md pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:hover:shadow-lg"
              >
                {isLoading ? 'Signing In...' : 'Sign In'}
              </button>

              <div className="text-center text-sm text-gray-600 mt-6">
                Don&apos;t have an account?{' '}
                <a href="/register" className="text-blue-600 font-semibold hover:text-blue-800 hover:underline transition-colors">
                  Sign Up
                </a>
              </div>
            </form>
          </div>
        </div>

        {/* Right Side - ML Agent Information */}
        <div className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 p-12 flex flex-col justify-center text-white relative overflow-hidden">
          {/* Decorative geometric shapes */}
          <div className="absolute top-10 right-10 w-20 h-20 border border-green-400 rounded-lg transform rotate-12 opacity-30"></div>
          <div className="absolute bottom-20 left-10 w-6 h-6 bg-yellow-400 rounded-full opacity-40"></div>
          <div className="absolute top-1/3 left-1/4 w-3 h-3 bg-green-400 rounded-full opacity-50"></div>

          {/* Main illustration area */}
          <div className="relative mb-8">
            <div className="w-80 h-80 mx-auto relative">
              {/* Hexagonal background */}
              <div className="absolute inset-0 border-2 border-green-400 opacity-20" style={{
                clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
              }}></div>
              
              {/* Character illustration placeholder */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-32 h-32 bg-gradient-to-b from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
                  <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center">
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="text-center space-y-6 relative z-10">
            <h2 className="text-4xl font-bold mb-4">Your Intelligent ML Agent</h2>
            <p className="text-xl text-gray-300 mb-8">
              Empower your data with our advanced machine learning capabilities
            </p>

            {/* Feature list */}
            <div className="space-y-4 text-left max-w-md mx-auto">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Data Processing:</span> Upload your datasets and let our agent analyze and process your data intelligently
                </p>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Code Execution:</span> Our agent can execute custom code to manipulate and transform your data according to your needs
                </p>
              </div>
              
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Real-time Analysis:</span> Get instant insights and results from your data processing tasks
                </p>
              </div>
            </div>

            {/* Progress indicators */}
            <div className="flex justify-center space-x-2 mt-8">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
              <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;