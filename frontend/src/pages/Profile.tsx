import React, { useState, useEffect } from 'react'
import './Profile.css'

const Profile: React.FC = () => {
  const profilePhoto = '/photo_2025-11-02_16-55-28.jpg'
  const [hasAchievement, setHasAchievement] = useState(false)

  useEffect(() => {
    // Слушаем событие о прохождении первого теста
    const handleFirstTestCompleted = () => {
      setHasAchievement(true)
    }
    
    window.addEventListener('firstTestCompleted', handleFirstTestCompleted)
    
    return () => {
      window.removeEventListener('firstTestCompleted', handleFirstTestCompleted)
    }
  }, [])

  return (
    <div className="profile-container">
      <h2 className="profile-title">Профиль</h2>
      
      <div className="profile-content">
        <div className="profile-photo-section">
          {profilePhoto ? (
            <img src={profilePhoto} alt="Фото профиля" className="profile-photo" />
          ) : (
            <div className="profile-photo-placeholder">
              <span>Нет фото</span>
            </div>
          )}
        </div>

        <div className="profile-info-section">
          <div className="profile-info-column">
            <div className="profile-info-column-left">
              <div className="profile-info-item">
                <div className="profile-info-label">Ваше имя</div>
                <div className="profile-info-value">Артем Смирнов</div>
              </div>

              <div className="profile-info-item">
                <div className="profile-info-label">Ваш уровень</div>
                <div className="profile-info-value">Новичок</div>
              </div>
            </div>

            <div className="profile-info-column-right">
              <div className="profile-info-item">
                <div className="profile-info-label">Ваш наставник</div>
                <div className="profile-info-value">Антон Нестеренко</div>
              </div>

              <div className="profile-info-item">
                <div className="profile-info-label">Ваша роль</div>
                <div className="profile-info-value">Cотрудник</div>
              </div>
            </div>
          </div>

          <div className="profile-achievements">
            <div className="achievements-title">Ваши достижения</div>
            <div className="achievements-placeholder">
              <div className="achievements-grid">
                <img src="/first.png" alt="Достижение 1" className="achievement-medal" />
                {hasAchievement && (
                  <img src="/2.png" alt="Достижение 2" className="achievement-medal" />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile

