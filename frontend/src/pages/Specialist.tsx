import React, { useState } from 'react'
import './Specialist.css'
import { API_ENDPOINTS } from '../apiConfig'

const Specialist: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedModule, setSelectedModule] = useState<number>(1)
  const [isUploading, setIsUploading] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleModuleClick = (moduleNum: number) => {
    setSelectedModule(moduleNum)
  }

  const handleChangeTest = async () => {
    if (!selectedFile) {
      alert('Пожалуйста, выберите файл документации')
      return
    }

    setIsUploading(true)
    
    // Небольшая задержка перед отправкой запроса
    await new Promise(resolve => setTimeout(resolve, 800))
    
    try {
      const response = await fetch(API_ENDPOINTS.updateModule, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          module: selectedModule,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      await response.json()
      alert(`Модуль ${selectedModule} успешно обновлен!`)
      
      setSelectedFile(null)
      
      // Сброс input файла
      const fileInput = document.getElementById('file-input') as HTMLInputElement
      if (fileInput) {
        fileInput.value = ''
      }
    } catch (error) {
      console.error('Ошибка при обновлении модуля:', error)
      alert(error instanceof Error ? error.message : 'Произошла ошибка при обновлении модуля')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="specialist-container">
      <div>
        <h2 className="page-title">Панель специалиста</h2>
        <p className="muted">Загрузка документации и управление тестами</p>
      </div>

      <div className="specialist-form-container">
        <div className="form-group">
          <label htmlFor="file-input" className="form-label">
            Загрузить документацию <span className="required">*</span>
          </label>
          <div className="file-upload-wrapper">
            <input
              type="file"
              id="file-input"
              className="file-input"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt"
            />
            <label htmlFor="file-input" className="file-upload-label">
              {selectedFile ? (
                <span className="file-name">📄 {selectedFile.name}</span>
              ) : (
                <span className="file-placeholder">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                  </svg>
                  Выберите файл для загрузки
                </span>
              )}
            </label>
          </div>
          {selectedFile && (
            <div className="file-info">
              Размер: {(selectedFile.size / 1024).toFixed(2)} KB
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">
            Выбор модуля <span className="required">*</span>
          </label>
          <div className="module-buttons">
            {Array.from({ length: 10 }, (_, i) => i + 1).map((moduleNum) => (
              <button
                key={moduleNum}
                type="button"
                className={`module-button ${selectedModule === moduleNum ? 'selected' : ''}`}
                onClick={() => handleModuleClick(moduleNum)}
              >
                Модуль {moduleNum}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          className="form-submit-btn change-test-btn"
          onClick={handleChangeTest}
          disabled={isUploading}
        >
          {isUploading ? 'Загрузка...' : 'Поменять тест'}
        </button>
      </div>
    </div>
  )
}

export default Specialist

