import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getCompliance, getGovernance } from '../api'

export default function ModelDetail(){
  const { id = '' } = useParams()
  const {data:comp} = useQuery({queryKey:['comp',id], queryFn:()=>getCompliance(id)})
  const {data:gov} = useQuery({queryKey:['gov',id], queryFn:()=>getGovernance(id)})

  return (
    <div className="grid">
      <div className="card">
        <h2>{id}</h2>
        <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(comp,null,2)}</pre>
      </div>
      <div className="card">
        <h3>Governance Report</h3>
        <pre style={{whiteSpace:'pre-wrap',maxHeight:500,overflow:'auto'}}>{JSON.stringify(gov,null,2)}</pre>
      </div>
    </div>
  )
}
