import { Sankey, Tooltip, ResponsiveContainer, Layer, Text } from 'recharts'

const PALETTE = ['#83a598','#fe8019','#b8bb26','#d3869b','#8ec07c','#fabd2f','#fb4934','#458588','#98971a']

export default function SankeyChart({nodes, links}:{nodes:{name:string}[], links:{source:number,target:number,value:number}[]}){
  const coloredNodes = nodes.map((n, i)=>({ ...n, color: PALETTE[i % PALETTE.length] }))
  return (
    <div style={{height:420}}>
      <ResponsiveContainer width="100%" height="100%">
        {/* @ts-ignore recharts types */}
        <Sankey data={{ nodes: coloredNodes, links }} nodePadding={24} linkCurvature={0.5}
          node={{ stroke: '#3c3836' }} link={{ stroke: '#504945', opacity: 0.6 }}
          nodeWidth={12} iterations={64}
          // @ts-ignore allow fill per node via payload
          // recharts Sankey uses node.fill if present
        >
          <Tooltip contentStyle={{ background:'#1d2021', border:'1px solid #3c3836', color:'#ebdbb2' }}/>
          <Layer>
            {coloredNodes.map((n:any, i:number)=>
              <Text key={i} x={(n as any).x + 14} y={(n as any).y + ((n as any).height||0)/2} textAnchor="start" fill="#ebdbb2" fontSize={12}>{n.name}</Text>
            )}
          </Layer>
        </Sankey>
      </ResponsiveContainer>
    </div>
  )
}
