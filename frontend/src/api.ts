function delay(ms:number){ return new Promise(res=>setTimeout(res, ms)) }

export async function getAllModels() {
  await delay(250)
  const r = await fetch('/api/v1/models?skip=0&limit=50')
  if(!r.ok) throw new Error('http')
  return r.json() as Promise<{total_models:number,models:any[]}>
}
export async function getGovernance(id:string){
  await delay(200)
  const r = await fetch(`/api/v1/models/${encodeURIComponent(id)}/governance_report`)
  if(!r.ok) throw new Error('http')
  return r.json()
}
export async function getCompliance(id:string){
  await delay(200)
  const r = await fetch(`/api/v1/models/${encodeURIComponent(id)}/compliance`)
  if(!r.ok) throw new Error('http')
  return r.json()
}
export async function getLists(){
  await delay(250)
  const [proh, sys, dep] = await Promise.all([
    fetch('/api/v1/models/prohibited').then(r=>r.json()),
    fetch('/api/v1/models/systemic_risk').then(r=>r.json()),
    fetch('/api/v1/models/deployable').then(r=>r.json()),
  ])
  return {proh, sys, dep} as {proh:string[], sys:string[], dep:string[]}
}
