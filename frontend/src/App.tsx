import { Route, Routes, NavLink, useNavigate } from 'react-router-dom'
import Overview from './pages/Overview'
import Models from './pages/Models'
import ModelDetail from './pages/ModelDetail'
import Policies from './pages/Policies'
import Compare from './pages/Compare'
import Analytics from './pages/Analytics'

export default function App(){
  const nav = useNavigate()
  return (
    <div>
      <div className="toolbar" style={{justifyContent:'space-between'}}>
        <div style={{display:'flex',gap:12,alignItems:'center'}}>
          <strong>Cyprus Console</strong>
          <NavLink to="/" end>Overview</NavLink>
          <NavLink to="/models">Models</NavLink>
          <NavLink to="/policies">Policies</NavLink>
          <NavLink to="/compare">Compare</NavLink>
          <NavLink to="/analytics">Analytics</NavLink>
        </div>
        <div style={{display:'flex',gap:8}}>
          <input placeholder="Search models..." onKeyDown={(e)=>{if(e.key==='Enter'){nav(`/models?q=${encodeURIComponent((e.target as HTMLInputElement).value)}`)}}} />
        </div>
      </div>
      <div className="container">
        <Routes>
          <Route path="/" element={<Overview/>} />
          <Route path="/models" element={<Models/>} />
          <Route path="/models/:id" element={<ModelDetail/>} />
          <Route path="/policies" element={<Policies/>} />
          <Route path="/compare" element={<Compare/>} />
          <Route path="/analytics" element={<Analytics/>} />
        </Routes>
      </div>
    </div>
  )
}
