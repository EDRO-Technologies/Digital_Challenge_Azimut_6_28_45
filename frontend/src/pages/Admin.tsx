import React, { useState, useEffect } from 'react'
import './Admin.css'
import { API_ENDPOINTS, API_CONFIG } from '../apiConfig'

interface User {
  id: number
  name: string
  role: string
  mentor: string | null
  lvl: string
}

const Admin: React.FC = () => {
  const [userForm, setUserForm] = useState({
    name: '',
    role: 'сотрудник',
    mentor: '',
    lvl: ''
  })

  const [users, setUsers] = useState<User[]>([])
  const [isLoadingUsers, setIsLoadingUsers] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setIsLoadingUsers(true)
    try {
      const response = await fetch(API_ENDPOINTS.users, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }))
        throw new Error(errorData.error || 'Ошибка при загрузке пользователей')
      }
      
      const data = await response.json()
      if (Array.isArray(data)) {
        setUsers(data)
      } else if (data.results && Array.isArray(data.results)) {
        setUsers(data.results)
      } else {
        setUsers(data.users || [])
      }
    } catch (error) {
      console.error('Ошибка при загрузке пользователей:', error)
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        console.warn(`Бэкенд сервер недоступен. Убедитесь, что сервер запущен на ${API_CONFIG.baseURL}`)
        setUsers([])
      } else {
        setUsers([])
      }
    } finally {
      setIsLoadingUsers(false)
    }
  }

  const deleteUser = async (userId: number) => {
    if (!confirm(`Вы уверены, что хотите удалить пользователя?`)) {
      return
    }

    try {
      const response = await fetch(API_ENDPOINTS.deleteUser(userId), {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }))
        throw new Error(errorData.error || 'Ошибка при удалении пользователя')
      }

      await loadUsers()
      alert('Пользователь успешно удален')
    } catch (error) {
      console.error('Ошибка при удалении пользователя:', error)
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        alert(`Бэкенд сервер недоступен. Убедитесь, что сервер запущен на ${API_CONFIG.baseURL}`)
      } else {
        alert(error instanceof Error ? error.message : 'Произошла ошибка при удалении пользователя')
      }
    }
  }

  const handleUserFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setUserForm(prev => {
      if (name === 'role' && value !== 'сотрудник') {
        return { ...prev, [name]: value, mentor: '' }
      }
      return { ...prev, [name]: value }
    })
  }

  const handleUserFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!userForm.name.trim()) {
      alert('Пожалуйста, заполните все обязательные поля')
      return
    }

    if (userForm.role === 'сотрудник' && !userForm.mentor.trim()) {
      alert('Пожалуйста, укажите наставника для сотрудника')
      return
    }

    try {
      const response = await fetch(API_ENDPOINTS.users, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: userForm.name,
          role: userForm.role,
          mentor: userForm.role === 'сотрудник' ? userForm.mentor : null,
          lvl: userForm.lvl || ''
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Ошибка сервера' }))
        throw new Error(errorData.error || 'Ошибка при добавлении пользователя')
      }

      const data = await response.json()
      alert(data.message || 'Пользователь успешно добавлен!')
      
      setUserForm({
        name: '',
        role: 'сотрудник',
        mentor: '',
        lvl: ''
      })

      await loadUsers()
    } catch (error) {
      console.error('Ошибка при добавлении пользователя:', error)
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        alert(`Бэкенд сервер недоступен. Убедитесь, что сервер запущен на ${API_CONFIG.baseURL}`)
      } else {
        alert(error instanceof Error ? error.message : 'Произошла ошибка при добавлении пользователя')
      }
    }
  }

  return (
    <div className="admin-container">
      <div>
        <h2 className="page-title">Панель администратора</h2>
        <p className="muted">Управление пользователями системы</p>
      </div>
      
      <div className="admin-form-container">
        <h3 className="form-title">Добавить нового пользователя</h3>
        <form onSubmit={handleUserFormSubmit} className="user-form">
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              Имя пользователя <span className="required">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={userForm.name}
              onChange={handleUserFormChange}
              className="form-input"
              placeholder="Введите имя пользователя"
              required
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label htmlFor="role" className="form-label">
              Роль <span className="required">*</span>
            </label>
            <select
              id="role"
              name="role"
              value={userForm.role}
              onChange={handleUserFormChange}
              className="form-select"
              required
            >
              <option value="администратор">Администратор</option>
              <option value="ментор">Ментор</option>
              <option value="специалист">Специалист</option>
              <option value="сотрудник">Сотрудник</option>
            </select>
          </div>

          {userForm.role === 'сотрудник' && (
            <div className="form-group">
              <label htmlFor="mentor" className="form-label">
                Наставник <span className="required">*</span>
              </label>
              <input
                type="text"
                id="mentor"
                name="mentor"
                value={userForm.mentor}
                onChange={handleUserFormChange}
                className="form-input"
                placeholder="Введите имя наставника"
                required
                maxLength={100}
              />
            </div>
          )}

          <button type="submit" className="form-submit-btn">
            Добавить пользователя
          </button>
        </form>
      </div>

      <div className="users-list-container">
        <h3 className="form-title">Список пользователей</h3>
        {isLoadingUsers ? (
          <div className="loading-message">Загрузка...</div>
        ) : users.length === 0 ? (
          <div className="empty-message">
            Пользователи не найдены
            <div className="backend-hint">
              💡 Убедитесь, что бэкенд сервер запущен на {API_CONFIG.baseURL}
            </div>
          </div>
        ) : (
          <div className="users-table">
            <div className="users-table-header">
              <div className="table-cell">ID</div>
              <div className="table-cell">Имя</div>
              <div className="table-cell">Роль</div>
              <div className="table-cell">Наставник</div>
              <div className="table-cell">Уровень</div>
              <div className="table-cell">Действие</div>
            </div>
            {users.map((user) => (
              <div key={user.id} className="users-table-row">
                <div className="table-cell">{user.id}</div>
                <div className="table-cell">{user.name}</div>
                <div className="table-cell">{user.role}</div>
                <div className="table-cell">{user.mentor || '-'}</div>
                <div className="table-cell">{user.lvl || '-'}</div>
                <div className="table-cell">
                  <button
                    className="delete-btn"
                    onClick={() => deleteUser(user.id)}
                    title="Удалить пользователя"
                  >
                    🗑️ Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Admin
