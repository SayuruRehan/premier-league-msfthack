import type {Audience,Cue} from './types';

export type TourStop={id:string;second:number;headline:string;audience:Audience};

export function buildTourStops(cues:Cue[]):TourStop[]{
  const goals=cues.filter(c=>c.kind==='goal');
  const shifts=cues.filter(c=>c.kind==='tactical_shift');
  const choices=[goals[0],shifts[0],goals[goals.length-1]].filter((c):c is Cue=>Boolean(c));
  const unique=choices.filter((cue,index)=>choices.findIndex(c=>c.id===cue.id)===index);
  const audiences:Audience[]=['fan','analyst','broadcast'];
  return unique.map((cue,index)=>({
    id:cue.id,second:cue.second,headline:cue.headline,audience:audiences[index%audiences.length],
  }));
}
