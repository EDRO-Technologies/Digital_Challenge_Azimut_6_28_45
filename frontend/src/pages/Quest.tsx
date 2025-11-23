import React, { useState, useEffect } from 'react'
import './Quest.css'
import { API_ENDPOINTS } from '../apiConfig'

const levels = [
  { id: 0, x: 214.19, y: 86, width: 231, height: 230, image: '3452.png', title: 'История и миссия', moduleId: 1 },
  { id: 1, x: 845.19, y: 169, width: 221, height: 221, image: '3458.png', title: 'Структура и активы', moduleId: 2 },
  { id: 2, x: 1500.19, y: 98, width: 206, height: 206, image: '34528.png', title: 'Технологии и модернизация', moduleId: 3 },
  { id: 3, x: 1464.19, y: 390, width: 242, height: 242, image: '34248.png', title: 'Безопасность и экология', moduleId: 4 },
  { id: 4, x: 1075.19, y: 676, width: 270, height: 270, image: '34548.png', title: 'Персонал и корпоративная культура', moduleId: 5 },
  { id: 5, x: 172.19, y: 511, width: 300, height: 300, image: '421344458.png', title: 'Социальная ответственность', moduleId: 6 },
  { id: 6, x: 429.19, y: 746, width: 266, height: 266, image: '3521458.png', title: 'Инновации и цифровизация', moduleId: 7 },
  { id: 7, x: 1243.19, y: 883, width: 351, height: 350, image: '4213458.png', title: 'Экономика и эффективность', moduleId: 8 },
  { id: 8, x: 906.19, y: 439, width: 283, height: 283, image: '32458.png', title: 'Перспективы и стратегия', moduleId: 9 },
  { id: 9, x: 218.19, y: 952, width: 316, height: 317, image: '34558.png', title: 'Регламенты и нормативная документация', moduleId: 10 },
]

interface Question {
  q: string
  o: string[]
  c?: number
  w?: number[]
}

interface ModuleData {
  module_id: number
  module_name: string
  questions: Question[]
  total_questions: number
}

interface TestModalProps {
  level: typeof levels[0] | null
  onClose: () => void
  onTestComplete: (levelId: number, percentage: number, moduleId: number) => void
  onCalibrationComplete?: (skippedModules: number[]) => void
}

const TestModal: React.FC<TestModalProps> = ({ level, onClose, onTestComplete, onCalibrationComplete }) => {
  const [moduleData, setModuleData] = useState<ModuleData | null>(null)
  const [loading, setLoading] = useState(true)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<{ 
    skipped_modules: number[], 
    message: string,
    correctCount?: number,
    totalQuestions?: number,
    wrongAnswers?: number[]
  } | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (level) {
      loadModule(level.moduleId)
    }
  }, [level])

  const loadModule = async (moduleId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(API_ENDPOINTS.getModule(moduleId))
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setModuleData(data)
      // Инициализируем ответы пустыми значениями
      const initialAnswers: Record<string, number> = {}
      data.questions.forEach((_: Question, index: number) => {
        initialAnswers[`question${index + 1}`] = -1
      })
      setAnswers(initialAnswers)
    } catch (err) {
      console.error('Ошибка при загрузке модуля:', err)
      setError('Не удалось загрузить тест. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerChange = (questionIndex: number, answerIndex: number) => {
    setAnswers(prev => ({ ...prev, [`question${questionIndex + 1}`]: answerIndex }))
  }

  const handleSubmit = async () => {
    if (!moduleData) return

    setIsSubmitting(true)
    try {
      // Если это калибровочный тест (модуль 0), отправляем на анализ
      if (moduleData.module_id === 0) {
        // Формируем ответы для API
        const answersForAPI: Record<string, string> = {}
        moduleData.questions.forEach((question, index) => {
          const answerIndex = answers[`question${index + 1}`]
          if (answerIndex >= 0 && question.o[answerIndex]) {
            answersForAPI[`question${index + 1}`] = question.o[answerIndex]
          }
        })

        try {
          const response = await fetch(API_ENDPOINTS.analyzeCalibration, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answers: answersForAPI }),
          })

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }

          const analysisData = await response.json()
          
          const skippedModules = analysisData.skipped_modules || []
          const message = skippedModules.length > 0
            ? `${analysisData.message || 'Калибровочный тест завершен'}. Модули ${skippedModules.join(', ')} засчитаны на 100%.`
            : analysisData.message || 'Калибровочный тест завершен'
          
          setResult({
            skipped_modules: skippedModules,
            message: message,
            correctCount: 0,
            totalQuestions: moduleData.questions.length,
            wrongAnswers: [],
          })

          // Вызываем callback для засчитывания модулей на 100%
          if (onCalibrationComplete) {
            onCalibrationComplete(analysisData.skipped_modules || [])
          }
        } catch (err) {
          console.error('Ошибка при анализе калибровочного теста:', err)
          alert('Произошла ошибка при анализе калибровочного теста.')
        } finally {
          setIsSubmitting(false)
        }
        return
      }

      // Для обычных тестов проверяем правильность ответов
      let correctCount = 0
      const totalQuestions = moduleData.questions.length
      const wrongAnswers: number[] = []

      moduleData.questions.forEach((question, index) => {
        const answerIndex = answers[`question${index + 1}`]
        if (question.c !== undefined && answerIndex === question.c) {
          correctCount++
        } else if (question.c !== undefined) {
          wrongAnswers.push(index + 1)
        }
      })

      const percentage = Math.round((correctCount / totalQuestions) * 100)
      const message = `Вы ответили правильно на ${correctCount} из ${totalQuestions} вопросов (${percentage}%)`
      
      setResult({
        skipped_modules: [],
        message: message,
        correctCount,
        totalQuestions,
        wrongAnswers,
      })

      // Сохраняем результат
      if (level) {
        onTestComplete(level.id, percentage, level.moduleId)
      }
    } catch (err) {
      console.error('Ошибка при проверке теста:', err)
      alert('Произошла ошибка при проверке теста.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!level) return null

  const allQuestionsAnswered = moduleData?.questions.every((_, index) => 
    answers[`question${index + 1}`] !== undefined && answers[`question${index + 1}`] >= 0
  ) ?? false

  return (
    <div 
      className="test-modal-overlay" 
      onClick={onClose}
      style={{ pointerEvents: 'auto' }}
    >
      <div className="test-modal" onClick={(e) => e.stopPropagation()}>
        <button className="test-modal-close" onClick={onClose}>×</button>
        
        {loading ? (
          <div className="test-loading">
            <p>Загрузка теста...</p>
          </div>
        ) : error ? (
          <div className="test-error">
            <p>{error}</p>
            <button className="test-close-btn" onClick={onClose}>Закрыть</button>
          </div>
        ) : !result && moduleData ? (
          <>
            <h2 className="test-modal-title">{moduleData.module_name}</h2>
            <p className="test-modal-subtitle">Вопросов: {moduleData.total_questions}</p>
            
            <div className="test-questions">
              {moduleData.questions.map((question, questionIndex) => (
                <div key={questionIndex} className="test-question">
                  <label className="test-question-label">
                    {questionIndex + 1}. {question.q}
                  </label>
                  <div className="test-options">
                    {question.o.map((option, optionIndex) => (
                      <label key={optionIndex} className="test-option">
                        <input
                          type="radio"
                          name={`question-${questionIndex}`}
                          value={optionIndex}
                          checked={answers[`question${questionIndex + 1}`] === optionIndex}
                          onChange={() => handleAnswerChange(questionIndex, optionIndex)}
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <button 
              className="test-submit-btn"
              onClick={handleSubmit}
              disabled={isSubmitting || !allQuestionsAnswered}
            >
              {isSubmitting ? 'Отправка...' : 'Отправить ответы'}
            </button>
          </>
        ) : result ? (
          <div className="test-result">
            <h3 className="test-result-title">Результаты теста</h3>
            <p className="test-result-message">{result.message}</p>
            {result.skipped_modules && result.skipped_modules.length > 0 && (
              <div className="test-result-modules">
                <p>Модули, засчитанные на 100%: {result.skipped_modules.join(', ')}</p>
              </div>
            )}
            {result.wrongAnswers && result.wrongAnswers.length > 0 && (
              <div className="test-result-modules">
                <p>Неправильные ответы на вопросы: {result.wrongAnswers.join(', ')}</p>
              </div>
            )}
            {result.correctCount !== undefined && result.totalQuestions !== undefined && result.totalQuestions > 0 && (
              <div className="test-result-score">
                <div className="test-score-bar">
                  <div 
                    className="test-score-fill" 
                    style={{ width: `${(result.correctCount / result.totalQuestions) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
            <button className="test-close-btn" onClick={onClose}>Закрыть</button>
          </div>
        ) : null}
      </div>
    </div>
  )
}

const Quest: React.FC = () => {
  const [selectedLevel, setSelectedLevel] = useState<typeof levels[0] | null>(null)
  const [levelResults, setLevelResults] = useState<Record<number, number>>({})
  const [showAchievementNotification, setShowAchievementNotification] = useState(false)
  const [hasFirstTestCompleted, setHasFirstTestCompleted] = useState(false)
  const [calibrationCompleted, setCalibrationCompleted] = useState(false)

  const handleLevelClick = (level: typeof levels[0]) => {
    setSelectedLevel(level)
  }

  const handleCloseModal = () => {
    setSelectedLevel(null)
  }

  const handleTestComplete = (levelId: number, percentage: number, moduleId: number) => {
    const newResults = { ...levelResults, [levelId]: percentage }
    setLevelResults(newResults)
    // Все работает в рамках одной сессии - не сохраняем в localStorage
    
    // Проверяем, был ли пройден первый тест (кроме калибровочного)
    if (moduleId !== 0 && !hasFirstTestCompleted) {
      setHasFirstTestCompleted(true)
      setShowAchievementNotification(true)
      // Отправляем событие для обновления Profile
      window.dispatchEvent(new CustomEvent('firstTestCompleted'))
    }
  }

  const handleCalibrationComplete = (skippedModules: number[]) => {
    // Отмечаем калибровочный тест как завершенный в рамках сессии
    setCalibrationCompleted(true)
    
    // skipped_modules - это модули, которые нужно сразу засчитать на 100%
    const newResults = { ...levelResults }
    skippedModules.forEach((moduleId) => {
      // Находим уровень с этим moduleId и устанавливаем 100%
      const level = levels.find(l => l.moduleId === moduleId)
      if (level) {
        newResults[level.id] = 100
      }
    })
    setLevelResults(newResults)
    
    // Калибровочный тест не дает достижение - только обычные тесты
    // Закрываем модальное окно
    setSelectedLevel(null)
  }

  return (
    <div className={`quest-container ${!calibrationCompleted ? 'calibration-pending' : ''}`}>
      {/* Оверлей с кнопкой запуска калибровочного теста (сверху) */}
      {!calibrationCompleted && !selectedLevel && (
        <div className='calibration-block'>
          <div className="calibration-overlay">
            <button
              className="calibration-button"
              onClick={() => {
                const calibrationLevel = { id: -1, x: 0, y: 0, width: 0, height: 0, image: '', title: 'Калибровочный тест', moduleId: 0 }
                setSelectedLevel(calibrationLevel as typeof levels[0])
              }}
            >
              Пройти калибровочный тест
            </button>
          </div>
        </div>
      )}

      {/* SVG с дорогами */}
      <svg className="quest-svg" viewBox="0 0 1914 1710" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Vector 1 */}
        <path 
          d="M301 170.763C364.963 167.175 507.686 120.388 474 254.729C445.919 366.714 718.5 231.729 936 247.729" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 6 */}
        <path 
          d="M301 671C356.5 718.5 350.407 711.396 316.721 845.737C288.64 957.722 319.221 976.5 521.221 919.5" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 2 */}
        <path 
          d="M964 228.762C1027.96 225.175 1002.11 344.145 1137 312.729C1226 292 1433 160 1638.5 160" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 7 */}
        <path 
          d="M549 906.546C730.5 787.046 792.605 730.812 928.5 757.545C989.5 769.545 990.5 838.544 1196 838.544" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 3 */}
        <path 
          d="M1638 522.5C1701.96 518.913 1759.5 449 1684.5 371.5C1579.67 263.18 1909.5 169 1667.5 169" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 5 */}
        <path 
          d="M320.229 631C242.171 557.182 422.125 564.854 496.444 557.182C544.766 552.193 869.439 651.726 1012 611.157" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 4 */}
        <path 
          d="M1066.5 619C1135.5 589 1128.94 635.296 1228 538.499C1337.5 431.5 1538.5 607 1620.5 534.5" 
          stroke="black" 
          strokeWidth="3"
        />

        {/* Vector 9 */}
        <path 
          d="M1246.5 833.953C1310.46 830.365 1377.66 807.875 1508.5 762.452C1737.5 682.952 1625 1048.88 1467.5 1083M1384 1083C1342.17 1052.83 1224 1025.25 1120 1158.45C990.001 1324.95 805.889 1219.23 678.501 1151.45C577.001 1097.45 466 1093.45 440 1120.95" 
          stroke="black" 
          strokeWidth="3"
        />
      </svg>

      {/* Карточки уровней */}
      {levels.map((level) => {
        // Не показываем калибровочный тест на карте (он открывается автоматически)
        if (level.moduleId === 0) {
          return null
        }
        
        const percentage = levelResults[level.id] || 0
        const isPassed = percentage >= 40
        // Все модули всегда доступны для прохождения
        
        return (
          <div
            key={level.id}
            className={`level-card level-${level.id} ${isPassed ? 'level-passed' : 'level-not-passed'}`}
            style={{
              left: `${(level.x / 1914) * 100}%`,
              top: `${(level.y / 1710) * 100}%`,
              width: `${(level.width / 1914) * 100}%`,
              maxWidth: `${level.width}px`,
            }}
            onClick={() => handleLevelClick(level)}
          >
            <div className="level-image-wrapper">
              <img 
                src={`/Levels/${level.image}`}
                alt={level.title}
                className="level-image"
                style={{
                  filter: isPassed ? 'none' : 'grayscale(100%)',
                }}
              />
            </div>
            <div className="level-info">
              <h3 className="level-title">
                {level.title}
                {level.moduleId !== 0 && (
                  <span className="level-percentage"> ({percentage}%)</span>
                )}
              </h3>
            </div>
          </div>
        )
      })}

      {/* Модальное окно с тестом */}
      {selectedLevel && (
        <TestModal
          level={selectedLevel}
          onClose={handleCloseModal}
          onTestComplete={handleTestComplete}
          onCalibrationComplete={handleCalibrationComplete}
        />
      )}

      {/* Уведомление о достижении */}
      {showAchievementNotification && (
        <div className="achievement-notification">
          <div className="achievement-notification-content">
            <h3>🎉 Поздравляем!</h3>
            <p>Вы получили достижение! Перейдите в профиль, чтобы увидеть медаль.</p>
            <button onClick={() => setShowAchievementNotification(false)}>Закрыть</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Quest
