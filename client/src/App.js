import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom'

function App() {

  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    async function checkSession() {
      const response = await fetch('/check_session')
      if (response.ok) {
        const data = await response.json()
        setCurrentUser( data )
      }
    }
    checkSession()
  }, [])

  return (
    <div className="App">
      <header className="App-header">

      </header>
      <Outlet context={[currentUser, setCurrentUser]}/>
    </div>
  );
}

export default App;
