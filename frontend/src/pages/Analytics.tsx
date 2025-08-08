import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getAllModels } from '../api'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis, Legend, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import SankeyChart from '../components/Sankey'

const COLORS = ['#83a598','#fe8019','#b8bb26','#d3869b','#8ec07c','#fabd2f','#fb4934']

export default function Analytics(){
  const {data} = useQuery({queryKey:['models-50'], queryFn:getAllModels})
  const [logScale, setLogScale] = useState(true)

  const points = useMemo(()=>{
    return (data?.models||[]).map((m:any)=>{
      const id = m.model_id || m.id || m.name || m.model
      const compute = Number(m.compute_flops || m.compute || m.params || m.flops || 0)
      const risk = Number(m.risk_score || m.risk || 0)
      const org = m.organization || m.org || 'unknown'
      const family = m.family || m.model_family || 'unknown'
      const rc = m.risk_category || 'unknown'
      const deployable = m.is_deployable ? 'deployable' : 'non-deployable'
      return { id, compute: isFinite(compute)?compute:0, risk: isFinite(risk)?risk:0, org, family, rc, deployable }
    })
  },[data])

  const byOrg = useMemo(()=>{
    const acc:Record<string,number> = {}
    points.forEach(p=>{acc[p.org]=(acc[p.org]||0)+1})
    return Object.entries(acc).map(([name,value])=>({name,value}))
  },[points])

  const byRiskCat = useMemo(()=>{
    const acc:Record<string,number> = {}
    points.forEach(p=>{acc[p.rc]=(acc[p.rc]||0)+1})
    return Object.entries(acc).map(([name,value])=>({name,value}))
  },[points])

  const sankeyData = useMemo(()=>{
    const orgs = Array.from(new Set(points.map(p=>p.org)))
    const deploy = ['deployable','non-deployable']
    const riskCats = Array.from(new Set(points.map(p=>p.rc||'unknown')))
    const sysNodes = ['systemic','non-systemic']
    const buckets = (v:number)=>{
      if(v<=1e11) return '<=1e11'; if(v<=1e12) return '<=1e12'; if(v<=1e13) return '<=1e13'; if(v<=1e14) return '<=1e14'; return '>1e14'
    }
    const computeBuckets = Array.from(new Set(points.map(p=>buckets(p.compute))))

    const nodeNames = [
      ...orgs,
      ...computeBuckets,
      ...sysNodes,
      ...riskCats,
      ...deploy
    ]
    const nodes = nodeNames.map(n=>({name:n}))
    const idx = (name:string)=>nodeNames.indexOf(name)

    const links: {source:number,target:number,value:number}[] = []

    orgs.forEach((o)=>{
      computeBuckets.forEach((cb)=>{
        const value = points.filter(p=>p.org===o && buckets(p.compute)===cb).length
        if(value>0) links.push({source: idx(o), target: idx(cb), value})
      })
    })

    computeBuckets.forEach((cb)=>{
      sysNodes.forEach((sn)=>{
        const value = points.filter(p=>buckets(p.compute)===cb && (sn==='systemic' ? p.rc==='systemic_risk' : p.rc!=='systemic_risk')).length
        if(value>0) links.push({source: idx(cb), target: idx(sn), value})
      })
    })

    sysNodes.forEach((sn)=>{
      riskCats.forEach((rc)=>{
        const value = points.filter(p=>(sn==='systemic' ? p.rc==='systemic_risk' : p.rc!=='systemic_risk') && (p.rc||'unknown')===rc).length
        if(value>0) links.push({source: idx(sn), target: idx(rc), value})
      })
    })

    riskCats.forEach((rc)=>{
      deploy.forEach((d)=>{
        const value = points.filter(p=>(p.rc||'unknown')===rc && p.deployable===d).length
        if(value>0) links.push({source: idx(rc), target: idx(d), value})
      })
    })

    return {nodes, links}
  },[points])

  return (
    <div className="grid">
      <div className="card" style={{height:420}}>
        <div className="toolbar">
          <strong>Compute vs Risk</strong>
          <label><input type="checkbox" checked={logScale} onChange={e=>setLogScale(e.target.checked)} /> log x-axis</label>
        </div>
        <ResponsiveContainer width="100%" height="80%">
          <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
            <CartesianGrid stroke="#3c3836" />
            <XAxis type="number" dataKey="compute" name="compute" stroke="#bdae93" tick={{fill:'#bdae93'}} scale={logScale? 'log':'auto'} domain={[ 'auto', 'auto' ]} />
            <YAxis type="number" dataKey="risk" name="risk" stroke="#bdae93" tick={{fill:'#bdae93'}} domain={[ 'auto', 'auto' ]} />
            <ZAxis type="category" dataKey="family" />
            <Tooltip cursor={{ stroke: '#fabd2f' }} contentStyle={{ background:'#1d2021', border:'1px solid #3c3836', color:'#ebdbb2' }} />
            <Legend />
            <Scatter name="models" data={points} fill="#fe8019" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{height:420}}>
        <div className="toolbar"><strong>Models by Organization</strong></div>
        <ResponsiveContainer width="100%" height="80%">
          <BarChart data={byOrg}>
            <CartesianGrid stroke="#3c3836" />
            <XAxis dataKey="name" stroke="#bdae93" tick={{fill:'#bdae93'}} interval={0} angle={-30} textAnchor="end" height={70}/>
            <YAxis stroke="#bdae93" tick={{fill:'#bdae93'}} />
            <Tooltip contentStyle={{ background:'#1d2021', border:'1px solid #3c3836', color:'#ebdbb2' }}/>
            <Bar dataKey="value" fill="#83a598" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{height:420}}>
        <div className="toolbar"><strong>Risk Category Breakdown</strong></div>
        <ResponsiveContainer width="100%" height="80%">
          <PieChart>
            <Pie data={byRiskCat} dataKey="value" nameKey="name" outerRadius={120}>
              {byRiskCat.map((e, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="#3c3836" />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background:'#1d2021', border:'1px solid #3c3836', color:'#ebdbb2' }}/>
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <div className="toolbar"><strong>Org → Deployability Sankey</strong></div>
        <SankeyChart nodes={sankeyData.nodes} links={sankeyData.links} />
      </div>
    </div>
  )
}
