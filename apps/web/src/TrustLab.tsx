import {useState} from 'react';
import type {Story} from './types';

export type FailureId = 'fabricated_claim'|'provider_outage'|'invalid_style';
export type TrustCase = {
  label:string;question:string;simulated_provider_output:string;
  expected_behavior:string;story:Story;
};
export type TrustLabData = {
  version:number;synthetic:boolean;simulated_failure_tests:boolean;
  live_model_inference:boolean;execution:string;seed:number;
  insight_id:string;cases:Record<FailureId,TrustCase>;
};

const CASES:FailureId[]=['fabricated_claim','provider_outage','invalid_style'];

export function TrustLab({data}:{data:TrustLabData}){
  const [selected,setSelected]=useState<FailureId>('fabricated_claim');
  if(!data.simulated_failure_tests || data.live_model_inference!==false) {
    return <p role="alert">Invalid simulation provenance: Trust Lab is unavailable.</p>;
  }
  const failure=data.cases[selected];
  if(!failure)return <p role="alert">Missing failure scenario.</p>;
  const story=failure.story;
  return <section className="v4-panel trust-lab" aria-label="Agent Trust Lab">
    <div className="v4-panel-head">
      <div className="eyebrow">06 / SAFETY AND RECOVERY</div>
      <h2>Agent Trust Lab</h2>
      <p className="trust-disclosure">SIMULATED TEST RESPONSES · NO LIVE PHI INFERENCE</p>
    </div>
    <div className="trust-content">
      <p className="trust-intro">Real Microsoft Agent Framework steps. Controlled provider responses. Select a failure to inspect the rejection and safe recovery.</p>
      <div className="trust-choices">
        {CASES.map(id=><button key={id} type="button"
          aria-pressed={selected===id}
          className={selected===id?'active':''}
          onClick={()=>setSelected(id)}>{data.cases[id].label}</button>)}
      </div>
      <div className="trust-case" data-testid="trust-case">
        <div className="trust-question">{failure.question}</div>
        <div className="trust-proposal-label">UNTRUSTED TEST INPUT · NOT A MODEL OUTPUT</div>
        <code className="trust-proposal">{failure.simulated_provider_output}</code>
        <p className="trust-expected">{failure.expected_behavior}</p>
        <div className="trust-verified">
          <strong>✓ VERIFIED RESULT</strong>
          <span>DIRECTOR: {story.source.toUpperCase()} · AUDIENCE: {story.style_source.toUpperCase()}</span>
        </div>
        <p className="trust-narration">{story.narration}</p>
        <div className="trust-trace-heading">ACTUAL WORKFLOW TRACE · {story.trace.length} STEPS</div>
        <div className="trust-trace">
          {story.trace.map((step,i)=><div key={i} className={'trust-step '+step.status}>
            <span className="trust-step-marker">{step.status==='rejected'?'×':step.status==='fallback'?'↻':'✓'}</span>
            <div><strong>{step.stage}</strong><small>{step.detail}</small></div>
            <span className="trust-step-status">{step.status}</span>
          </div>)}
        </div>
        <div className="trust-proof">{story.evidence_event_ids.length} source event IDs preserved · simulated match evidence</div>
      </div>
    </div>
  </section>;
}
