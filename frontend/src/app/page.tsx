'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import StatCard from '@/components/dashboard/StatCard'
import ProgressBarCard from '@/components/dashboard/ProgressBarCard'
import DonutChartCard from '@/components/dashboard/DonutChartCard'

interface DashboardStats {
  total_applicants: number
  score_distribution: {
    excellent: number
    good: number
    fair: number
    poor: number
    not_eligible: number
  }
  average_score: number
  approval_rate: number
}

export default function Home() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected'>('disconnected')

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/dashboard/stats')
        if (response.ok) {
          const data = await response.json()
          setStats(data)
          setBackendStatus('connected')
        } else {
          throw new Error('Failed to fetch stats')
        }
      } catch (error) {
        console.error('Error fetching stats:', error)
        // Use demo data if backend is not available
        setStats({
          total_applicants: 10000,
          score_distribution: {
            excellent: 1800,
            good: 2700,
            fair: 3000,
            poor: 1500,
            not_eligible: 1000
          },
          average_score: 625,
          approval_rate: 0.75
        })
        setBackendStatus('disconnected')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const handleGenerateDemoUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/demo/generate-users?count=50')
      if (response.ok) {
        const result = await response.json()
        alert(`Generated ${result.generated} demo users! Refreshing dashboard...`)
        window.location.reload()
      }
    } catch (error) {
      console.error('Error generating demo users:', error)
      alert('Could not connect to backend. Make sure it\'s running on port 8000.')
    }
  }

  const donutData = stats ? [
    { name: 'Excellent', value: stats.score_distribution.excellent, color: '#10B981' },
    { name: 'Good', value: stats.score_distribution.good, color: '#3B82F6' },
    { name: 'Fair', value: stats.score_distribution.fair, color: '#F59E0B' },
    { name: 'Poor', value: stats.score_distribution.poor, color: '#EF4444' },
    { name: 'Not Eligible', value: stats.score_distribution.not_eligible, color: '#6B7280' }
  ] : []

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header 
          title="IntelliCredit Dashboard"
          subtitle="AI-Powered Alternate Credit Scoring"
        />
        
        <main className="flex-1 overflow-y-auto p-6">
          {/* Backend Status Banner */}
          <div className={`mb-6 p-4 rounded-lg ${
            backendStatus === 'connected' 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-yellow-50 border border-yellow-200'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={`font-semibold ${
                  backendStatus === 'connected' ? 'text-green-800' : 'text-yellow-800'
                }`}>
                  Backend {backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </p>
                <p className={`text-sm ${
                  backendStatus === 'connected' ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {backendStatus === 'connected' 
                    ? 'Live data from ML scoring engine' 
                    : 'Showing demo data - Start backend for live scoring'}
                </p>
              </div>
              <button
                onClick={handleGenerateDemoUsers}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Generate Demo Users
              </button>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : stats ? (
            <>
              {/* Key Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                <StatCard
                  label="Credit-Invisible Adults"
                  value="190M+"
                  change="+Untapped"
                  isPositive={true}
                />
                <StatCard
                  label="Potential Lending Market"
                  value="₹3.5L Cr"
                  change="+High Growth"
                  isPositive={true}
                />
                <StatCard
                  label="First-Time Rejections"
                  value="90%"
                  change="-Problem"
                  isPositive={false}
                />
                <StatCard
                  label="Scoring Time"
                  value="30 Sec"
                  change="+Real-time"
                  isPositive={true}
                />
              </div>

              {/* Charts Row */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <ProgressBarCard
                  title="Score Distribution"
                  data={[
                    { name: 'Excellent (750-850)', value: (stats.score_distribution.excellent / stats.total_applicants) * 100, count: stats.score_distribution.excellent },
                    { name: 'Good (650-749)', value: (stats.score_distribution.good / stats.total_applicants) * 100, count: stats.score_distribution.good },
                    { name: 'Fair (550-649)', value: (stats.score_distribution.fair / stats.total_applicants) * 100, count: stats.score_distribution.fair },
                    { name: 'Poor (450-549)', value: (stats.score_distribution.poor / stats.total_applicants) * 100, count: stats.score_distribution.poor },
                    { name: 'Not Eligible (<450)', value: (stats.score_distribution.not_eligible / stats.total_applicants) * 100, count: stats.score_distribution.not_eligible }
                  ]}
                />
                
                <DonutChartCard
                  title="Applicant Breakdown"
                  data={donutData}
                />
              </div>

              {/* How It Works Section */}
              <div className="bg-white rounded-xl shadow-md p-6 mb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">How IntelliCredit Works</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="text-3xl mb-2">🔐</div>
                    <h3 className="font-semibold text-blue-800 mb-2">1. Consent Layer</h3>
                    <p className="text-sm text-blue-700">
                      Users explicitly consent to each data source individually. DPDP Act 2023 compliant with partial consent support.
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="text-3xl mb-2">⚙️</div>
                    <h3 className="font-semibold text-green-800 mb-2">2. Six Data Workers</h3>
                    <p className="text-sm text-green-700">
                      Parallel processing of UPI/Bank, Telecom, E-commerce, Geolocation, Questionnaire, and Merchant/GST data.
                    </p>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <div className="text-3xl mb-2">🤖</div>
                    <h3 className="font-semibold text-purple-800 mb-2">3. ML Engine + SHAP</h3>
                    <p className="text-sm text-purple-700">
                      Two-tier XGBoost+LightGBM ensemble with isotonic calibration. Every score comes with explainable SHAP breakdowns.
                    </p>
                  </div>
                </div>
              </div>

              {/* Score Bands Table */}
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Score Bands & Outcomes</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Band</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Range</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Outcome</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4"><span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-2"></span>Excellent</td>
                        <td className="py-3 px-4 font-mono">750-850</td>
                        <td className="py-3 px-4 text-green-600 font-medium">Best Terms</td>
                        <td className="py-3 px-4 text-sm text-gray-600">Instant approval, lowest rates</td>
                      </tr>
                      <tr className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4"><span className="inline-block w-3 h-3 rounded-full bg-blue-500 mr-2"></span>Good</td>
                        <td className="py-3 px-4 font-mono">650-749</td>
                        <td className="py-3 px-4 text-blue-600 font-medium">Standard</td>
                        <td className="py-3 px-4 text-sm text-gray-600">Approved with standard rates</td>
                      </tr>
                      <tr className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4"><span className="inline-block w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>Fair</td>
                        <td className="py-3 px-4 font-mono">550-649</td>
                        <td className="py-3 px-4 text-yellow-600 font-medium">Higher Rate</td>
                        <td className="py-3 px-4 text-sm text-gray-600">Smaller loan, elevated interest</td>
                      </tr>
                      <tr className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4"><span className="inline-block w-3 h-3 rounded-full bg-red-400 mr-2"></span>Poor</td>
                        <td className="py-3 px-4 font-mono">450-549</td>
                        <td className="py-3 px-4 text-red-600 font-medium">Limited</td>
                        <td className="py-3 px-4 text-sm text-gray-600">Very small loans only</td>
                      </tr>
                      <tr className="hover:bg-gray-50">
                        <td className="py-3 px-4"><span className="inline-block w-3 h-3 rounded-full bg-gray-400 mr-2"></span>Not Eligible</td>
                        <td className="py-3 px-4 font-mono">&lt;450</td>
                        <td className="py-3 px-4 text-gray-600 font-medium">Rejected</td>
                        <td className="py-3 px-4 text-sm text-gray-600">SHAP breakdown + improvement plan</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Failed to load dashboard data</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
