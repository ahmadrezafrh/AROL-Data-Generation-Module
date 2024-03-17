import {Route, Routes } from 'react-router-dom'
import GenerateDataPage from '../generate/pages/GenerateDataPage'

export default function Router () {

  function getRoute (path: string) {
    switch (path) {
      case '/generate': {
        return <GenerateDataPage/>
      }
    }
  }

  return (         
        <Routes>    
            <Route
                path="/"
                element={getRoute('/generate')}/>
            <Route
                path="/generate"
                element={getRoute('/generate')}
            />
        </Routes>
  )
}
