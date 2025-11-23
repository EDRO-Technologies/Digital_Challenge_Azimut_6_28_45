import React, { useEffect, useRef, useState } from 'react'
import './Chat.css'
import botAvatar from '../assets/bot_avatar.png';
import helloVideo from '../assets/hello_circle.MOV';
import { API_ENDPOINTS } from '../apiConfig';

type Message = {
  id: string
  sender: 'bot' | 'user'
  text?: string 
  video?: string  
}

const initialBotMessage: Message = { id: 'b:0', video: helloVideo, sender: 'bot' }

const TelegramVideoPlayer: React.FC<{ src: string }> = ({ src }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showControls, setShowControls] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleEnded = () => {
    setIsPlaying(false);
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    e.stopPropagation();
    if (videoRef.current) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percent = x / rect.width;
      videoRef.current.currentTime = percent * duration;
    }
  };

  return (
    <div 
      className="telegram-video-container"
      onMouseEnter={() => { setIsHovered(true); setShowControls(true); }}
      onMouseLeave={() => { setIsHovered(false); setTimeout(() => setShowControls(false), 2000); }}
      onClick={togglePlay}
    >
      <video
        ref={videoRef}
        src={src}
        className="message-video"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
      >
        Ваш браузер не поддерживает видео.
      </video>
      
      {!isPlaying && (
        <div className="telegram-play-button">
          <svg width="60" height="60" viewBox="0 0 60 60" fill="none">
            <circle cx="30" cy="30" r="30" fill="rgba(0, 0, 0, 0.6)"/>
            <path d="M24 20L24 40L40 30L24 20Z" fill="white"/>
          </svg>
        </div>
      )}

      {showControls && isHovered && (
        <div className="telegram-video-controls" onClick={(e) => e.stopPropagation()}>
          <div className="telegram-progress-bar">
            <div 
              className="telegram-progress-track" 
              onClick={handleProgressClick}
            >
              <div 
                className="telegram-progress-fill" 
                style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>
          </div>
          <div className="telegram-time-info">
            <span>{formatTime(currentTime)} / {formatTime(duration)}</span>
          </div>
        </div>
      )}
    </div>
  );
};

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([initialBotMessage])
  const [inputValue, setInputValue] = useState<string>('')
  const messagesRef = useRef<HTMLDivElement>(null)

  // Закомментировано до необходимости
  // const [isRecording, setIsRecording] = useState(false);
  // const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  // const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    // scroll to bottom when messages change
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight
    }
  }, [messages])

  function addMessage(text: string, sender: Message['sender'], id?: string) {
    const msg: Message = { id: id || String(Date.now()) + Math.random().toString(16).slice(2), text, sender }
    setMessages(prev => [...prev, msg])
  }

  async function sendMessage(text?: string) {
    const message = (text ?? inputValue).trim()
    if (!message) return
    setInputValue('')

    addMessage(message, 'user')

    const botTempId = 'b:' + Date.now() + Math.random().toString(16).slice(2)
    const botTemp = { id: botTempId, text: '', sender: 'bot' } as Message
    setMessages(prev => [...prev, botTemp])

    try {
      const response = await fetch(API_ENDPOINTS.getAnswer, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const reply = data.answer; // API returns { "answer": "...", "metadata": [] }

      setMessages(prev => prev.map(m => m.id === botTempId ? { ...m, text: reply } : m));

    } catch (error) {
      console.error("Error fetching bot response:", error);
      setMessages(prev => prev.map(m => m.id === botTempId ? { ...m, text: 'Извините, произошла ошибка при получении ответа.' } : m));
    }
  }

  // Закомментировано до необходимости
  // const startRecording = async () => {
  //   try {
  //     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  //     mediaRecorderRef.current = new MediaRecorder(stream);
  //     audioChunksRef.current = [];

  //     mediaRecorderRef.current.ondataavailable = (event) => {
  //       audioChunksRef.current.push(event.data);
  //     };

  //     mediaRecorderRef.current.onstop = async () => {
  //       const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
  //       const formData = new FormData();
  //       formData.append('file', audioBlob, 'audio.webm');

  //       const botTempId = 'b:' + Date.now() + Math.random().toString(16).slice(2);
  //       const botTemp = { id: botTempId, text: '', sender: 'bot' } as Message;
  //       setMessages(prev => [...prev, botTemp]);

  //       try {
          
  //         const response = await fetch("http://5.53.21.135:8021/speech_to_text", {
  //           method: 'POST',
  //           body: formData,
  //         });

  //         if (!response.ok) {
  //           throw new Error(`HTTP error! status: ${response.status}`);
  //         }

  //         const data = await response.json();
  //         const transcribedText = data.text; // Assuming the API returns { "text": "..." }

  //         // addMessage(transcribedText, 'user'); // Удалено, чтобы избежать дублирования
  //         sendMessage(transcribedText); // Отправляем транскрибированный текст как обычное сообщение

  //       } catch (error) {
  //         console.error("Error sending audio for transcription:", error);
  //         setMessages(prev => prev.map(m => m.id === botTempId ? { ...m, text: 'Извините, произошла ошибка при распознавании речи.' } : m));
  //       }
  //     };

  //     mediaRecorderRef.current.start();
  //     setIsRecording(true);
  //   } catch (err) {
  //     console.error('Ошибка при доступе к микрофону:', err);
  //   }
  // };

  // const stopRecording = () => {
  //   mediaRecorderRef.current?.stop();
  //   setIsRecording(false);
  // };

  // function sendQuickMessage(text: string) {
  //   sendMessage(text)
  // }

  return (
    <div className="chat-container">
      <h2 className="chat-title">Чат-помощник для адаптации новых сотрудников!</h2>
      <div className="chat-messages" ref={messagesRef}>
        {messages.map(m => {
          const isSending = m.text === '' && m.id.startsWith('b:')
          const rowClass = `message-row ${m.sender === 'bot' ? 'bot-row' : 'user-row'}`
          const bubbleClass = `bubble ${m.sender === 'bot' ? 'bot-bubble' : 'user-bubble'} ${isSending ? 'sending' : ''}`
          return (
            <div key={m.id} className={rowClass}>
              {m.sender === 'bot' && (
                <img src={botAvatar} alt="Bot" className="message-avatar" />
              )}
              <div className={bubbleClass}>
                {m.video ? (
                  <TelegramVideoPlayer src={m.video} />
                ) : isSending ? (
                  <span className="dots">
                    <span></span><span></span><span></span>
                  </span>
                ) : (
                  m.text
                )}
              </div>
              {m.sender === 'user' && (
                <div className="message-avatar" />
              )}
            </div>
          )
        })}
      </div>

      {/* <div className="quick-buttons">
        <button className="quick-btn" onClick={() => sendQuickMessage('Какие СИЗ нужны для работы с химикатами?')}>🎯 СИЗ для химикатов</button>
        <button className="quick-btn" onClick={() => sendQuickMessage('Что делать при пожаре?')}>🔥 Действия при пожаре</button>
        <button className="quick-btn" onClick={() => sendQuickMessage('Правила работы на высоте')}>🪜 Работа на высоте</button>
      </div> */}

      <div className="chat-input-container">
        <input
          className="chat-input"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') sendMessage() }}
          placeholder="Введите ваш вопрос..."
          aria-label="Введите сообщение"
        />
        <button 
          className="send-btn" 
          onClick={() => sendMessage()}
          aria-label="Отправить сообщение"
        >
          Отправить
        </button>
      </div>
    </div>
  )
}

export default Chat

