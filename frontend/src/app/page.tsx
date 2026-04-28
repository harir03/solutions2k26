import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import StatCard from '@/components/dashboard/StatCard'
import ProgressBarCard from '@/components/dashboard/ProgressBarCard'
import DonutChartCard from '@/components/dashboard/DonutChartCard'

export default function Home() {
  const stats = [
    { label: 'Credit-invisible adults', value: '190M+', change: '+2.5%', isPositive: true },
    { label: 'Potential lending market', value: '₹3.5L Cr', change: '+15%', isPositive: true },
    { label: 'Loan rejections (first-time)', value: '90%', change: '-5%', isPositive: false },
    { label: 'Avg. scoring time', value: '30 sec', change: '-10%', isPositive: true },
  ]

  const scoreDistribution = [
    { name: 'Excellent (750-850)', value: 18, count: 1800 },
    { name: 'Good (650-749)', value: 27, count: 2700 },
    { name: 'Fair (550-649)', value: 30, count: 3000 },
    { name: 'Poor (450-549)', value: 15, count: 1500 },
    { name: 'Not Eligible (<450)', value: 10, count: 1000 },
  ]

  return (
    <div className="min-h-screen bg-gray-900">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">IntelliCredit Dashboard</h1>
            <p className="text-gray-400">AI-powered alternate credit scoring for underserved India</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => (
              <StatCard
                key={index}
                label={stat.label}
                value={stat.value}
                change={stat.change}
                isPositive={stat.isPositive}
              />
            ))}
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <ProgressBarCard 
              title="Score Distribution"
              data={scoreDistribution}
            />
            <DonutChartCard
              title="Applicant Breakdown"
              data={scoreDistribution}
            />
          </div>

          {/* Info Section */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">How IntelliCredit Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-blue-400 font-medium mb-2">1. Consent Layer</h3>
                <p className="text-gray-400 text-sm">Users explicitly consent to each data source. DPDP Act 2023 compliant with partial consent support.</p>
              </div>
              <div>
                <h3 className="text-green-400 font-medium mb-2">2. Six Data Workers</h3>
                <p className="text-gray-400 text-sm">Parallel processing of UPI, telecom, e-commerce, geolocation, psychometric, and merchant data.</p>
              </div>
              <div>
                <h3 className="text-purple-400 font-medium mb-2">3. Fair ML Engine</h3>
                <p className="text-gray-400 text-sm">XGBoost + LightGBM blend with three-layer fairness enforcement and SHAP explainability.</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
