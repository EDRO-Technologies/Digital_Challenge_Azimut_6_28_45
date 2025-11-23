import React, { useState, useEffect } from 'react'
import './Mentor.css'
import { API_ENDPOINTS, API_CONFIG } from '../apiConfig'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface GeneralAnalytics {
  total_users: number
  total_tests: number
  successful_tests: number
  success_rate: number
  module_statistics: Array<{
    module_id: number
    successful_users: number
  }>
}

const Mentor: React.FC = () => {
  const [analytics, setAnalytics] = useState<GeneralAnalytics | null>(null)
  const [isLoadingModuleStats, setIsLoadingModuleStats] = useState(false)
  const [moduleStatsError, setModuleStatsError] = useState<string | null>(null)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    setIsLoadingModuleStats(true)
    setModuleStatsError(null)
    try {
      const response = await fetch(API_ENDPOINTS.generalAnalytics, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }))
        throw new Error(errorData.error || 'Ошибка при загрузке аналитики')
      }

      const data: GeneralAnalytics = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Ошибка при загрузке аналитики:', error)
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        setModuleStatsError(`Бэкенд сервер недоступен. Убедитесь, что сервер запущен на ${API_CONFIG.baseURL}`)
      } else {
        setModuleStatsError(error instanceof Error ? error.message : 'Произошла ошибка при загрузке аналитики')
      }
      setAnalytics(null)
    } finally {
      setIsLoadingModuleStats(false)
    }
  }

  const moduleChartData = analytics?.module_statistics
    ? analytics.module_statistics
        .sort((a, b) => a.module_id - b.module_id)
        .map(stat => ({
          name: `Модуль ${stat.module_id}`,
          users: stat.successful_users,
        }))
    : []

  return (
    <div className="mentor-container">
      <div>
        <h2 className="page-title">Аналитика для ментора Антона Нестеренко</h2>
        <p className="muted">Статистика по модулям</p>
      </div>

      {isLoadingModuleStats ? (
        <div className="loading-message">Загрузка статистики по модулям...</div>
      ) : moduleStatsError ? (
        <div className="error-message">
          {moduleStatsError}
          <div className="backend-hint">
            💡 Убедитесь, что бэкенд сервер запущен на {API_CONFIG.baseURL}
          </div>
        </div>
      ) : moduleChartData.length > 0 ? (
        <div className="analytics-content">
          <div className="chart-container">
            <h3 className="chart-title">Статистика по модулям</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={moduleChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  interval={0}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="users" fill="#27ae60" name="Количество пользователей" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="empty-message">Нет данных по модулям</div>
      )}
    </div>
  )
}

export default Mentor
