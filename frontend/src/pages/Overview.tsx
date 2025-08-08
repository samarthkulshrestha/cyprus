import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

async function fetchJSON<T>(url:string):Promise<T>{
  const r = await fetch(url)
  if(!r.ok) throw new Error('http')
  return r.json()
}

export default function Overview(){
  const {data:all} = useQuery({queryKey:['all-50'], queryFn:()=>fetchJSON<{total_models:number,models:any[]}>('/api/v1/models?skip=0&limit=50')})
  const {data:proh} = useQuery({queryKey:['proh-50'], queryFn:()=>fetchJSON<string[]>('/api/v1/models/prohibited')})
  const {data:sys} = useQuery({queryKey:['sys-50'], queryFn:()=>fetchJSON<string[]>('/api/v1/models/systemic_risk')})
  const {data:dep} = useQuery({queryKey:['dep-50'], queryFn:()=>fetchJSON<string[]>('/api/v1/models/deployable')})

  const idOf = (m:any)=>m.model_id||m.id||m.name||m.model
  const normalize = (s:string)=>decodeURIComponent(String(s))
  const limitedIds = new Set((all?.models||[]).map((m:any)=>normalize(idOf(m))))
  const depCount = (dep||[]).map(normalize).filter(id=>limitedIds.has(id)).length
  const prohCount = (proh||[]).map(normalize).filter(id=>limitedIds.has(id)).length
  const sysCount = (sys||[]).map(normalize).filter(id=>limitedIds.has(id)).length

  const counts = {
    total: all?.models?.length ?? 0,
    prohibited: prohCount,
    systemic: sysCount,
    deployable: depCount,
    nondeployable: Math.max(0, (all?.models?.length ?? 0) - depCount)
  }

  return (
    <div className="grid cols-3">
      <div className="card"><h3>Total Models</h3><div className="badge">{counts.total}</div></div>
      <div className="card"><h3>Prohibited</h3><div className="badge err">{counts.prohibited}</div></div>
      <div className="card"><h3>Systemic Risk</h3><div className="badge warn">{counts.systemic}</div></div>
      <div className="card"><h3>Deployable</h3><div className="badge ok">{counts.deployable}</div></div>
      <div className="card"><h3>Non-Deployable</h3><div className="badge">{counts.nondeployable}</div></div>
      <div className="card">
        <h3>Quick Links</h3>
        <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
          <Link to="/models">Explore Models</Link>
          <Link to="/policies">Policies</Link>
          <Link to="/analytics">Analytics</Link>
        </div>
      </div>
    </div>
  )
}
