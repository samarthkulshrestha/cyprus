import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useLocation } from 'react-router-dom'
import { getAllModels, getLists } from '../api'

function useQueryParam(name:string){
  const q = new URLSearchParams(useLocation().search)
  return q.get(name) || ''
}

export default function Models(){
  const {data} = useQuery({queryKey:['models-50'], queryFn:getAllModels})
  const {data:lists} = useQuery({queryKey:['lists'], queryFn:getLists})
  const q = useQueryParam('q').toLowerCase()
  const [filters,setFilters] = useState({ prohibited:false, systemic:false, deployable:false })

  const rows = useMemo(()=>{
    const ms = data?.models ?? []
    const prohibited = new Set(lists?.proh||[])
    const systemic = new Set(lists?.sys||[])
    const deployable = new Set(lists?.dep||[])
    return ms.filter((m:any)=>{
      const id = m.model_id || m.id || m.name || m.model
      if(q && !JSON.stringify(m).toLowerCase().includes(q)) return false
      if(filters.prohibited && !prohibited.has(id)) return false
      if(filters.systemic && !systemic.has(id)) return false
      if(filters.deployable && !deployable.has(id)) return false
      return true
    })
  },[data,lists,q,filters])

  return (
    <div>
      <div className="toolbar">
        <label><input type="checkbox" checked={filters.prohibited} onChange={e=>setFilters(f=>({...f,prohibited:e.target.checked}))}/> prohibited</label>
        <label><input type="checkbox" checked={filters.systemic} onChange={e=>setFilters(f=>({...f,systemic:e.target.checked}))}/> systemic risk</label>
        <label><input type="checkbox" checked={filters.deployable} onChange={e=>setFilters(f=>({...f,deployable:e.target.checked}))}/> deployable</label>
      </div>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Org</th>
              <th>Compute</th>
              <th>Family</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m:any)=>{
              const id = m.model_id || m.id || m.name || m.model
              const compute = m.compute_flops || m.compute || m.params || m.flops || '-'
              const family = m.family || m.model_family || '-'
              return (
                <tr key={id}>
                  <td><Link to={`/models/${encodeURIComponent(id)}`}>{id}</Link></td>
                  <td>{m.organization || m.org || '-'}</td>
                  <td>{compute}</td>
                  <td>{family}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
