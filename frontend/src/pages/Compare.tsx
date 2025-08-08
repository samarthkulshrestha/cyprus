import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getAllModels } from '../api'

export default function Compare(){
  const {data} = useQuery({queryKey:['models'], queryFn:getAllModels})
  const models = (data?.models||[]).map((m:any)=>m.id||m.name||m.model)
  const [a,setA] = useState('')
  const [b,setB] = useState('')
  return (
    <div className="card">
      <div className="toolbar">
        <select value={a} onChange={e=>setA(e.target.value)}><option value="">select A</option>{models.map((m:string)=><option key={m}>{m}</option>)}</select>
        <select value={b} onChange={e=>setB(e.target.value)}><option value="">select B</option>{models.map((m:string)=><option key={m}>{m}</option>)}</select>
      </div>
      <div className="grid cols-3">
        <div className="card"><h4>A</h4><pre>{JSON.stringify(data?.models.find((m:any)=>m.id===a||m.name===a||m.model===a)||{},null,2)}</pre></div>
        <div className="card"><h4>Δ</h4><p>diff coming soon</p></div>
        <div className="card"><h4>B</h4><pre>{JSON.stringify(data?.models.find((m:any)=>m.id===b||m.name===b||m.model===b)||{},null,2)}</pre></div>
      </div>
    </div>
  )
}
