import React, { useState } from 'react'
import './App.css'
import Chat from './pages/Chat'
import Quest from './pages/Quest'
import Specialist from './pages/Specialist'
import Mentor from './pages/Mentor'
import Admin from './pages/Admin'
import Profile from './pages/Profile'

const App: React.FC = () => {
  const [activePage, setActivePage] = useState<'chat' | 'quests' | 'admin' | 'specialist' | 'mentor' | 'profile'>('chat')

  function showPage(page: typeof activePage) {
    setActivePage(page)
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Ориентир</h1>
        <div className="user-info">
          <div className="avatar">АС</div>
        </div>
      </header>

      <nav className="top-nav">
        <button className={`nav-item ${activePage === 'chat' ? 'active' : ''}`} onClick={() => showPage('chat')}>
          <span>Чат-помощник</span>
        </button>
        <button className={`nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => showPage('profile')}>
          <span>Профиль</span>
        </button>
        <button className={`nav-item ${activePage === 'quests' ? 'active' : ''}`} onClick={() => showPage('quests')}>
          <span>Квесты</span>
        </button>
        <button className={`nav-item ${activePage === 'specialist' ? 'active' : ''}`} onClick={() => showPage('specialist')}>
          <span>Специалист</span>
        </button>
        <button className={`nav-item ${activePage === 'mentor' ? 'active' : ''}`} onClick={() => showPage('mentor')}>
          <span>"Наставник"</span>
        </button>
        <button className={`nav-item ${activePage === 'admin' ? 'active' : ''}`} onClick={() => showPage('admin')}>
          <span>АДМИНИСТРАТОР</span>
        </button>
      </nav>

      <main className="main-content">

        <section className={`page ${activePage === 'chat' ? 'active' : ''}`} aria-hidden={activePage !== 'chat'}>
          <Chat />
        </section>

        <section className={`page ${activePage === 'quests' ? 'active' : ''}`} aria-hidden={activePage !== 'quests'}>
          <Quest />
        </section>

        <section className={`page ${activePage === 'specialist' ? 'active' : ''}`} aria-hidden={activePage !== 'specialist'}>
          <Specialist />
        </section>

        <section className={`page ${activePage === 'mentor' ? 'active' : ''}`} aria-hidden={activePage !== 'mentor'}>
          <Mentor />
        </section>

        <section className={`page ${activePage === 'admin' ? 'active' : ''}`} aria-hidden={activePage !== 'admin'}>
          <Admin />
        </section>

        <section className={`page ${activePage === 'profile' ? 'active' : ''}`} aria-hidden={activePage !== 'profile'}>
          <Profile />
        </section>
      </main>
    </div>
  )
}

export default App
