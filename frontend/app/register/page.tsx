'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff, Check } from 'lucide-react';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

const RegisterPage: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  const [agreeToTerms, setAgreeToTerms] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRegistered, setIsRegistered] = useState<boolean>(false);
  const [isLoggingIn, setIsLoggingIn] = useState<boolean>(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // Auto-login function after successful registration
  const performAutoLogin = async (email: string, password: string) => {
    setIsLoggingIn(true);
    try {
      const response = await fetch('http://localhost:8003/api/v1/gateway/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Store the access token
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type);
        // Mark as new login to trigger session creation
        localStorage.setItem('isNewLogin', 'true');
        console.log('Auto-login successful');
        // Redirect to chat page
        router.push('/chat');
      } else {
        console.error('Auto-login failed');
        // If auto-login fails, show success message and redirect to login
        setIsRegistered(true);
      }
    } catch (error) {
      console.error('Auto-login error:', error);
      // If auto-login fails, show success message and redirect to login
      setIsRegistered(true);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!agreeToTerms) {
      alert('Please agree to the terms & conditions');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8003/api/v1/gateway/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      if (response.ok) {
        console.log('Registration successful');
        // Automatically log in the user after successful registration
        await performAutoLogin(formData.email, formData.password);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Registration failed:', errorData);
        if (response.status === 409) {
          alert('An account with this email already exists. Please use a different email or sign in.');
        } else {
          alert('Registration failed. Please try again.');
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration error. Please try again.');
    } finally {
      if (!isLoggingIn) {
        setIsLoading(false);
      }
    }
  };

  const handleLoginRedirect = () => {
    router.push('/login');
  };

  if (isRegistered) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl border-2 border-blue-100 p-12 max-w-md w-full text-center">
          <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg">
            <Check className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-6">Registration Successful!</h1>
          <p className="text-gray-600 mb-10 text-lg leading-relaxed">
            Your account has been created successfully. You can now log in with your credentials.
          </p>
          <button
            onClick={handleLoginRedirect}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl border-2 border-blue-100 overflow-hidden max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2">
        {/* Left Side - Registration Form */}
        <div className="p-12 flex flex-col justify-center">
          <div className="max-w-md w-full mx-auto">
            {/* Welcome Text */}
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Create Account</h1>
            <p className="text-gray-600 mb-8">Join our intelligent ML agent platform</p>

            {/* Registration Form */}
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

              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  placeholder="Confirm Password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-4 bg-blue-50 border-2 border-blue-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400 transition-all shadow-sm hover:shadow-md pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>

              {/* Terms and Conditions */}
              <div className="flex items-start space-x-3">
                <div className="flex items-center mt-1">
                  <input
                    type="checkbox"
                    id="terms"
                    checked={agreeToTerms}
                    onChange={(e) => setAgreeToTerms(e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-blue-50 border-blue-200 rounded focus:ring-blue-500 focus:ring-2"
                  />
                </div>
                <label htmlFor="terms" className="text-sm text-gray-600">
                  I agree to the{' '}
                  <a href="#" className="text-blue-600 font-semibold hover:text-blue-800 hover:underline transition-colors">
                    terms & conditions
                  </a>
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading || isLoggingIn || !agreeToTerms}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:hover:shadow-lg"
              >
                {isLoading && !isLoggingIn ? 'Creating Account...' : 
                 isLoggingIn ? 'Signing You In...' : 
                 'Create Account'}
              </button>

              <div className="text-center text-sm text-gray-600 mt-6">
                Already have an account?{' '}
                <a href="/login" className="text-blue-600 font-semibold hover:text-blue-800 hover:underline transition-colors">
                  Sign In
                </a>
              </div>
            </form>
          </div>
        </div>

        {/* Right Side - ML Agent Information */}
        <div className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 p-12 flex flex-col justify-center text-white relative overflow-hidden">
          {/* Decorative geometric shapes */}
          <div className="absolute top-10 right-10 w-20 h-20 border-2 border-blue-300 rounded-lg transform rotate-12 opacity-30"></div>
          <div className="absolute bottom-20 left-10 w-6 h-6 bg-blue-300 rounded-full opacity-40"></div>
          <div className="absolute top-1/3 left-1/4 w-3 h-3 bg-blue-200 rounded-full opacity-50"></div>

          {/* Main illustration area */}
          <div className="relative mb-8">
            <div className="w-80 h-80 mx-auto relative">
              {/* Hexagonal background */}
              <div className="absolute inset-0 border-2 border-blue-300 opacity-20" style={{
                clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
              }}></div>
              
              {/* Character illustration placeholder */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-32 h-32 bg-gradient-to-b from-white to-blue-100 rounded-full flex items-center justify-center shadow-xl">
                  <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="text-center space-y-6 relative z-10">
            <h2 className="text-4xl font-bold mb-4">Join Our ML Community</h2>
            <p className="text-xl text-gray-300 mb-8">
              Start your journey with intelligent data analysis
            </p>

            {/* Feature list */}
            <div className="space-y-4 text-left max-w-md mx-auto">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-300 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Smart Analytics:</span> Upload and analyze your datasets with advanced machine learning algorithms
                </p>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Code Generation:</span> Get custom Python code automatically generated for your data processing needs
                </p>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Interactive Chat:</span> Communicate with our AI agent to get insights and perform complex data operations
                </p>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-gray-300">
                  <span className="text-white font-semibold">Secure Platform:</span> Your data is protected with enterprise-grade security and privacy measures
                </p>
              </div>
            </div>

            {/* Progress indicators */}
            <div className="flex justify-center space-x-2 mt-8">
              <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;