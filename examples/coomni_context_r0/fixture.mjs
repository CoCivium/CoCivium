import {makeSyntheticSource} from './compiler.mjs';
export const sampleSources=[
  makeSyntheticSource('source:alpha','PRIOR','PUBLIC',['alpha','plan'],
    'Alpha plan records a proposed task and its original source.'),
  makeSyntheticSource('source:beta','CHALLENGE','PUBLIC',['alpha','challenge'],
    'Alpha plan has not been independently tested and may be wrong.'),
  makeSyntheticSource('source:gamma','TEST','PUBLIC',['alpha','test'],
    'Alpha can be tested using a deterministic comparison.'),
  makeSyntheticSource('source:delta','PRIOR','PUBLIC',['unrelated','history'],
    'Delta is another unrelated historical design.'),
  makeSyntheticSource('source:epsilon','PROPOSAL','LOCAL',['alpha','local'],
    'An alpha-related local-only proposal.'),
];
export const sampleWork={work_id:'work:alpha-analysis',query:'alpha plan test challenge',receiver:'PUBLIC',
  authority:'NONE',byte_budget:1700,max_items:3};
