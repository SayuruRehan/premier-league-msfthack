import type {Cue, MatchEvent, Replay, Story} from './types';
import {clock} from './types';

type Props={
  match:Replay;time:number;score:{home:number;away:number};trail:MatchEvent[];
  cue:Cue|undefined;story:Story|undefined;onSeek:(second:number)=>void;
};
const px=(x:number)=>25+x*9.5;
const py=(y:number)=>25+y*5.6;

export function BroadcastStage({match,time,score,trail,cue,story,onSeek}:Props){
  const latest=trail[trail.length-1];
  const validStory=story?.verified && story.insight_id===cue?.insight_id ? story : undefined;
  return <section className="broadcast-frame" aria-label="Fictional football match broadcast">
    <div className="broadcast-canvas">
      <svg viewBox="0 0 1000 610" role="img" aria-label="Synthetic football pitch showing the most recent action and evidence focus">
        <defs>
          <pattern id="broadcast-grass" width="125" height="610" patternUnits="userSpaceOnUse">
            <rect width="125" height="610" fill="#104b3d"/>
            <rect width="63" height="610" fill="#185a48"/>
          </pattern>
          <radialGradient id="spotlight-ring"><stop offset="0%" stopColor="#ceff90" stopOpacity=".2"/><stop offset="100%" stopColor="#ceff90" stopOpacity="0"/></radialGradient>
          <marker id="pass-arrow" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
            <path d="M0 0 L6 3 L0 6" fill="none" stroke="#f5ffdc" strokeWidth="1.3"/>
          </marker>
        </defs>
        <rect width="1000" height="610" fill="url(#broadcast-grass)"/>
        {Array.from({length:7},(_,i)=><rect key={i} x={i*145} y="0" width="7" height="610" fill="#ffffff" opacity=".02"/>)}
        <g stroke="#d9ede1" strokeWidth="3" fill="none" opacity=".65">
          <rect x="25" y="25" width="950" height="560"/>
          <path d="M500 25V585"/>
          <circle cx="500" cy="305" r="85"/>
          <path d="M25 160H180V450H25 M975 160H820V450H975"/>
          <path d="M25 235H85V375H25 M975 235H915V375H975"/>
          <circle cx="500" cy="305" r="4" fill="#d9ede1"/>
        </g>
        {trail.filter(e=>e.kind==='pass'&&e.target&&e.success).slice(-5).map((e,i)=>
          <line key={e.id} x1={px(e.position.x)} y1={py(e.position.y)}
            x2={px(e.target!.x)} y2={py(e.target!.y)}
            stroke="#f2ffdc" strokeWidth={i===4?3:1.8}
            opacity={.18+i*.13} strokeDasharray="9 7" markerEnd="url(#pass-arrow)"/>)}
        {trail.map((event,i)=>{
          const last=i===trail.length-1;
          return <g key={event.id}>
            <circle cx={px(event.position.x)} cy={py(event.position.y)} r={last?17:7}
              fill={event.team==='home'?'#adf0ff':'#ffc66d'}
              opacity={last?1:.18+(i/trail.length)*.5} stroke="#ffffff" strokeWidth={last?3:1}/>
            {last&&<circle cx={px(event.position.x)} cy={py(event.position.y)} r="29" fill="none"
              stroke="#ffffff" strokeOpacity=".55" strokeWidth="2" strokeDasharray="5 7"/>}
          </g>
        })}
        {cue&&<>
          <circle cx={px(cue.focus.x)} cy={py(cue.focus.y)} r="64" fill="url(#spotlight-ring)"/>
          <circle cx={px(cue.focus.x)} cy={py(cue.focus.y)} r="39" fill="none" stroke="#c0fb7b" strokeWidth="4" className="broadcast-pulse"/>
          <path d={`M${px(cue.focus.x)-36} ${py(cue.focus.y)-48} L${px(cue.focus.x)+35} ${py(cue.focus.y)-48}`} stroke="#c0fb7b" strokeWidth="3"/>
        </>}
      </svg>
      <div className="broadcast-top">
        <span className="onair"><span className="airdot"/> SYNTHETIC MATCH REPLAY</span>
        <div className="tv-score" aria-label="Current score">
          <span>NFC</span><strong>{score.home} — {score.away}</strong><span>HCT</span><b>{clock(time)}</b>
        </div>
      </div>
      {latest&&!cue&&<div className="broadcast-activity">{latest.kind.toUpperCase()} <b>{latest.player}</b><span>{clock(latest.second)}</span></div>}
      {cue&&<div className={'broadcast-lower-third '+(cue.kind==='goal'?'goal-banner':'tactical-banner')} aria-live="polite">
        <div className="broadcast-kicker"><span>{cue.kind==='goal'?'● GOAL MOMENT':'◈ TACTICAL TURNING POINT'}</span><span>{clock(cue.second)} · {validStory?'VERIFIED AGENT STORY':'EVENT-GROUNDED CUE'}</span></div>
        <h3>{validStory?.headline??cue.headline}</h3>
        <p>{validStory?.narration??cue.subtitle}</p>
        <div className="broadcast-facts"><span>{cue.metric_label}</span><strong>{cue.metric_value}</strong><span>{cue.evidence_event_ids.length} SOURCE EVENTS</span></div>
      </div>}
      {!cue&&time===0&&<div className="broadcast-prompt">
        <strong>Ready for kickoff</strong><span>Play the match or choose a highlight below.</span>
        {match.cues.length>0&&<button onClick={()=>onSeek(match.cues[0].second)}>Jump to first key moment →</button>}
      </div>}
      <div className="broadcast-watermark">MATCHSHIFT AI <span>·</span> NOT REAL PREMIER LEAGUE FOOTAGE</div>
    </div>
  </section>;
}
