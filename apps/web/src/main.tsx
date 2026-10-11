import React, {useEffect, useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {BroadcastStage} from './BroadcastStage';
import type {Audience, Replay, Story} from './types';
import {clock} from './types';
import {buildTourStops} from './tour';
import './style.css';

const API='/api/matches/demo';
const STATIC_MODE=import.meta.env.VITE_STATIC_DEMO==='true';
const STATIC_DATA_BASE=import.meta.env.BASE_URL+'data/';
function App(){
  const [match,setMatch]=useState<Replay|null>(null);
  const [error,setError]=useState('');
  const [time,setTime]=useState(0);
  const [playing,setPlaying]=useState(false);
  const [speed,setSpeed]=useState(30);
  const [audience,setAudience]=useState<Audience>('broadcast');
  const [focus,setFocus]=useState(false);
  const [tourOn,setTourOn]=useState(false);
  const [tourIndex,setTourIndex]=useState(0);
  const [stories,setStories]=useState<Record<string,Story>>({});
  const [storyLoading,setStoryLoading]=useState(false);
  const [storyError,setStoryError]=useState('');

  useEffect(()=>{
    const controller=new AbortController();
    const checkedJson=async(url:string)=>{
      const response=await fetch(url,{signal:controller.signal});
      if(!response.ok)throw new Error('Unable to load '+url+': '+response.status);
      return response.json();
    };
    if(STATIC_MODE){
      // Static visitors receive verified precomputed results, never model/API calls.
      Promise.all([checkedJson(STATIC_DATA_BASE+'replay.json'),checkedJson(STATIC_DATA_BASE+'stories.json')])
        .then(([replay,precomputed]:[Replay,Record<string,Story>])=>{
          if(controller.signal.aborted)return;
          setStories(precomputed);
          setMatch(replay);
        })
        .catch(err=>{if(!controller.signal.aborted)setError(String(err))});
    }else{
      checkedJson(API).then((data:Replay)=>setMatch(data))
        .catch(err=>{if(!controller.signal.aborted)setError(String(err))});
    }
    return ()=>controller.abort();
  },[]);

  useEffect(()=>{
    if(!match||!playing)return;
    const interval=window.setInterval(()=>setTime(previous=>Math.min(match.duration_seconds,previous+speed)),1000);
    return ()=>window.clearInterval(interval);
  },[match,playing,speed]);

  useEffect(()=>{
    if(match && time>=match.duration_seconds)setPlaying(false);
  },[time,match]);

  const events=useMemo(()=>match?.events.filter(e=>e.second<=time)??[],[match,time]);
  const score=useMemo(()=>({
    home:events.filter(e=>e.team==='home'&&e.kind==='goal').length,
    away:events.filter(e=>e.team==='away'&&e.kind==='goal').length,
  }),[events]);
  const insights=match?.insights.filter(i=>i.second<=time)??[];
  const activeInsight=insights[insights.length-1];
  const shownCues=match?.cues.filter(c=>c.second<=time&&time<c.until_second)??[];
  const liveCue=shownCues[shownCues.length-1];
  const snapshots=match?.snapshots.filter(s=>s.second<=time)??[];
  const snapshot=snapshots[snapshots.length-1];
  const storyKey=activeInsight ? activeInsight.id+':'+audience : '';
  const activeStory=stories[storyKey];

  useEffect(()=>{
    if(!activeInsight||activeStory){setStoryLoading(false);setStoryError('');return;}
    if(STATIC_MODE){
      setStoryLoading(false);
      setStoryError('Verified offline story unavailable for this highlight.');
      return;
    }
    let valid=true;
    const controller=new AbortController();
    setStoryLoading(true);
    setStoryError('');
    const query=new URLSearchParams({seed:'7',insight_id:activeInsight.id,audience});
    fetch(API+'/story?'+query.toString(),{signal:controller.signal})
      .then(response=>{if(!response.ok)throw new Error('Agent pipeline: '+response.status);return response.json()})
      .then((story:Story)=>{if(valid)setStories(previous=>({...previous,[storyKey]:story}))})
      .catch(err=>{if(valid)setStoryError(String(err))})
      .finally(()=>{if(valid)setStoryLoading(false)});
    return ()=>{valid=false;controller.abort()};
  },[activeInsight?.id,audience,activeStory,storyKey]);

  const tourStops=useMemo(()=>buildTourStops(match?.cues??[]),[match]);
  useEffect(()=>{
    if(!tourOn || tourStops.length===0)return;
    const timer=window.setTimeout(()=>{
      const next=tourIndex+1;
      if(next>=tourStops.length){setTourOn(false);return;}
      setTourIndex(next);
      setTime(tourStops[next].second);
      setAudience(tourStops[next].audience);
    },9000);
    return ()=>window.clearTimeout(timer);
  },[tourOn,tourIndex,tourStops]);

  function startTour(){
    if(!tourStops.length)return;
    setPlaying(false);
    setTourIndex(0);
    setTime(tourStops[0].second);
    setAudience(tourStops[0].audience);
    setTourOn(true);
  }

  function seek(second:number){setTourOn(false);setTime(second);setPlaying(false);}
  const last=events[events.length-1];
  const latestEvidence=(liveCue?.evidence_event_ids??activeInsight?.evidence_event_ids??[])
    .slice(-6).map(id=>match?.events.find(e=>e.id===id)).filter((e):e is NonNullable<typeof e>=>Boolean(e));
  const cueStory=liveCue?stories[liveCue.insight_id+':'+audience]:undefined;
  const nextCue=match?.cues.find(c=>c.second>time);
  const previousCue=match?.cues.filter(c=>c.second<time).slice(-1)[0];

  if(error)return <main className="error"><h1>Backend unavailable</h1><p>{error}</p><p>Start FastAPI on port 8000, then refresh.</p></main>;
  if(!match)return <main className="error"><h1>Loading broadcast studio…</h1></main>;

  return <main className={'shell v4'+(focus?' focus-mode':'')}>
    <header>
      <div className="brand"><span className="mark">M</span><div>
        <strong>MATCHSHIFT <span>AI</span></strong><small>INTELLIGENT MATCH STUDIO</small>
      </div></div>
      <div className="topright"><span className="dot"/> {STATIC_MODE?'PUBLIC OFFLINE DEMO':'FICTIONAL MATCH'}
        <span className="beta">JUDGE DEMO · V0.5</span>
      </div>
    </header>

    <section className="v4-hero">
      <div>
        <div className="eyebrow">MATCH INTELLIGENCE / THE BROADCAST EXPERIENCE</div>
        <h1>The game has a story.<br/><em>We show the why.</em></h1>
        <p>One simulated match. Evidence-backed broadcast cues. Verified stories orchestrated with Microsoft Agent Framework.</p>
      </div>
      <div className="match-card">
        <div className="match-card-title">SYNTHETIC FRIENDLY <span>DEMO MATCH 001</span></div>
        <div className="match-card-teams">
          <div><span className="v4-crest home">N</span><strong>{match.home_name}</strong></div>
          <div className="v4-result">{score.home} <span>:</span> {score.away}<small>{clock(time)}</small></div>
          <div><span className="v4-crest away">H</span><strong>{match.away_name}</strong></div>
        </div>
      </div>
    </section>

    <div className="v4-main">
      <div className="v4-left">
        <div className="v4-section-head">
          <div><span className="eyebrow">01 / LIVE REPLAY STUDIO</span><h2>Broadcast canvas</h2></div>
          <div className="v4-demo-actions">
            <button className="v4-tour-button" disabled={!tourStops.length}
              aria-label={tourOn?'Stop guided tour':'Start guided tour'}
              aria-pressed={tourOn} onClick={()=>tourOn?setTourOn(false):startTour()}>
              {tourOn?'■ Stop tour':'▶ Guided tour · 27s'}
            </button>
            <button className="v4-quiet-button" onClick={()=>setFocus(!focus)} aria-pressed={focus}>
              {focus?'◱ Exit focus view':'▣ Focus broadcast'}
            </button>
          </div>
        </div>
        {tourOn&&tourStops[tourIndex]&&<div className="v4-tour-status" role="status">
          <strong>GUIDED TOUR {tourIndex+1}/{tourStops.length}</strong>
          <span>{tourStops[tourIndex].headline} · {tourStops[tourIndex].audience.toUpperCase()} VIEW</span>
          <span>Auto-advances every 9 seconds</span>
        </div>}
        <BroadcastStage match={match} time={time} score={score} trail={events.slice(-12)}
          cue={liveCue} story={cueStory} onSeek={seek}/>

        <section className="v4-transport" aria-label="Match replay controls">
          <div className="v4-playback">
            <button className="v4-play" onClick={()=>{setTourOn(false);if(time===match.duration_seconds)setTime(0);setPlaying(!playing)}} aria-label={playing?'Pause match':'Play match'}>
              {playing?'Ⅱ Pause':'▶ Play'}
            </button>
            <div className="v4-play-controls">
              <button onClick={()=>previousCue&&seek(previousCue.second)} disabled={!previousCue} title="Previous highlight">← Previous</button>
              <button onClick={()=>nextCue&&seek(nextCue.second)} disabled={!nextCue} title="Next highlight">Next →</button>
            </div>
            <label htmlFor="replay-speed" className="sr-only">Playback speed</label>
            <select id="replay-speed" value={speed} onChange={e=>setSpeed(Number(e.target.value))}>
              <option value={15}>15×</option><option value={30}>30×</option><option value={90}>90×</option>
            </select>
          </div>
          <div className="v4-progress-wrap">
            <input id="replay-progress" aria-label="Replay time" type="range" min={0} max={match.duration_seconds}
              step={30} value={time} onChange={e=>seek(Number(e.target.value))}/>
            <div className="v4-timeline-dots">
              {match.cues.map(c=><button key={c.id} style={{left:(c.second/match.duration_seconds*100)+'%'}}
                className={'v4-tick '+c.kind} title={c.headline+' at '+clock(c.second)}
                aria-label={'Jump to '+c.headline+' at '+clock(c.second)}
                onClick={()=>seek(c.second)}/>)}
            </div>
            <div className="v4-clock"><span>{clock(time)}</span><span>90:00</span></div>
          </div>
        </section>

        <section className="v4-highlights">
          <div className="v4-section-head"><div>
            <span className="eyebrow">02 / DIRECTOR'S CUE SHEET</span>
            <h2>Match-changing moments</h2>
          </div><span className="v4-meta">{match.cues.length} VERIFIED CUES</span></div>
          <div className="v4-cue-list">
            {match.cues.map((c,i)=><button key={c.id}
              className={'v4-cue-card '+(liveCue?.id===c.id?'active':'')}
              onClick={()=>seek(c.second)} aria-label={'Jump to '+c.headline+' at '+clock(c.second)}>
              <span className="v4-cue-num">{String(i+1).padStart(2,'0')}</span>
              <span className={'v4-cue-icon '+c.kind}>{c.kind==='goal'?'⚽':'↗'}</span>
              <span className="v4-cue-copy"><strong>{c.headline}</strong><small>{c.kind==='goal'?'GOAL · '+clock(c.second):'TACTICAL SHIFT · '+clock(c.second)}</small></span>
              <span className="v4-cue-arrow">→</span>
            </button>)}
          </div>
        </section>
      </div>

      <aside className="v4-right">
        <section className="v4-panel">
          <div className="v4-panel-head"><div className="eyebrow">03 / TACTICAL SIGNALS</div><h2>Five-minute snapshot</h2></div>
          <div className="v4-team-metrics">
            {(['home','away'] as const).map(team=><div className="v4-team" key={team}>
              <div className="v4-team-title"><span className={'bullet '+team}/>{team==='home'?match.home_name:match.away_name}</div>
              <div><span>High regains</span><strong>{snapshot?.[team].high_regains??'—'}</strong></div>
              <div><span>Ball regains</span><strong>{snapshot?.[team].regains??'—'}</strong></div>
              <div><span>Pass accuracy</span><strong>{snapshot?.[team].pass_accuracy_pct==null?'—':snapshot[team].pass_accuracy_pct+'%'}</strong></div>
            </div>)}
          </div>
          <p className="v4-footnote">High regains are an event-location proxy, not measured real-world pressing or PPDA.</p>
        </section>

        <section className="v4-panel">
          <div className="v4-panel-head"><div className="eyebrow">04 / MICROSOFT AGENT FRAMEWORK</div><h2>Verified story control</h2></div>
          <div className="v4-audience">
            {(['fan','analyst','broadcast'] as const).map(a=><button key={a} onClick={()=>setAudience(a)}
              className={audience===a?'selected':''} aria-pressed={audience===a}>{a.toUpperCase()}</button>)}
          </div>
          <div className="v4-story">
            {!activeInsight?<div className="v4-placeholder">Choose a highlight to see the verified four-stage agent workflow.</div>:
              storyLoading&&!activeStory?<div className="v4-placeholder">Validating event evidence…</div>:
              storyError&&!activeStory?<p className="agenterror" role="alert">{storyError}</p>:activeStory?
                <><div className="v4-verified">✓ EVIDENCE VERIFIED <span>{activeStory.source==='foundry_local'?'PHI · FOUNDRY LOCAL':activeStory.source==='fallback'?'LOCAL MODEL FALLBACK':'FREE DETERMINISTIC MODE'}</span></div>
                <h3>{activeStory.headline}</h3><p>{activeStory.narration}</p>
                <div className="v4-trace-label">WORKFLOW TRACE · {activeStory.presentation_style.toUpperCase()} STYLE ({activeStory.style_source.toUpperCase()})</div>
                <div className="v4-trace">{activeStory.trace.map((t,i)=><div key={i}>
                  <span className={'v4-status '+t.status}>{t.status==='rejected'?'!':'✓'}</span>
                  <div><strong>{t.stage}</strong><small>{t.detail}</small></div>
                </div>)}</div></>:<div className="v4-placeholder">Fetching verified story…</div>}
          </div>
        </section>

        <section className="v4-panel">
          <div className="v4-panel-head"><div className="eyebrow">05 / SOURCE OF TRUTH</div><h2>Click-through evidence</h2></div>
          <div className="v4-evidence">
            {latestEvidence.length===0?<p className="v4-placeholder">Verified evidence appears after a match-changing moment.</p>:
              latestEvidence.map(e=><button key={e.id} onClick={()=>seek(e.second)} title={'Jump to '+e.id}>
                <span>{clock(e.second)}</span><strong>{e.kind.toUpperCase()} · {e.player}</strong><small>{e.id} ↗</small>
              </button>)}
          </div>
          <div className="v4-source-footer">{last?events.length:0} / {match.events.length} SYNTHETIC EVENTS OBSERVED</div>
        </section>
      </aside>
    </div>
    <footer>MATCHSHIFT AI <span>·</span> FICTIONAL FOOTBALL DATA ONLY <span>·</span> NO PREMIER LEAGUE FOOTAGE OR OFFICIAL FEED {STATIC_MODE?' · ALL AGENT STORIES PRECOMPUTED OFFLINE':''}</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
