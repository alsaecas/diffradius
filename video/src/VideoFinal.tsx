import React from 'react';
import {Audio} from '@remotion/media';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import content from './data/content.json';
import evidence from './data/evidence.json';

const F = 30;
const S = (n: number) => Math.round(n * F);
const color = {
  bg: '#080b10', panel: '#0f151e', text: '#f4f7fb', muted: '#8d9bad',
  line: '#263244', mint: '#8cf2cf', blue: '#73a7ff', red: '#ff8c95', amber: '#f2bd6d',
};
const sans = 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif';
const mono = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace';

const enter = (frame: number, delay = 0) => ({
  opacity: interpolate(frame, [delay, delay + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
  transform: `translateY(${interpolate(frame, [delay, delay + 24], [28, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  })}px)`,
});

const Backdrop: React.FC = () => (
  <AbsoluteFill style={{
    backgroundColor: color.bg,
    backgroundImage: 'linear-gradient(rgba(115,167,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(115,167,255,.035) 1px,transparent 1px)',
    backgroundSize: '72px 72px',
  }}>
    <div style={{position:'absolute', width:680, height:680, borderRadius:'50%', filter:'blur(145px)', background:color.mint, opacity:.07, left:-300, top:-300}} />
    <div style={{position:'absolute', width:620, height:620, borderRadius:'50%', filter:'blur(145px)', background:color.blue, opacity:.06, right:-280, bottom:-280}} />
  </AbsoluteFill>
);

const Logo: React.FC = () => (
  <div style={{display:'flex', alignItems:'center', gap:13, fontWeight:760, fontSize:25, letterSpacing:'-.03em'}}>
    <div style={{display:'flex', alignItems:'center', gap:4, transform:'rotate(-12deg)', height:30}}>
      {[15,30,21].map((h, i) => <i key={i} style={{width:7, height:h, borderRadius:8, background:`linear-gradient(${color.mint},${color.blue})`}} />)}
    </div>
    DiffRadius
  </div>
);

const Frame: React.FC<{kicker: string; children: React.ReactNode}> = ({kicker, children}) => (
  <AbsoluteFill style={{fontFamily:sans, color:color.text, padding:'58px 82px 55px'}}>
    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', paddingBottom:21, borderBottom:`1px solid ${color.line}`}}>
      <Logo />
      <span style={{fontFamily:mono, fontSize:14, letterSpacing:2.1, color:color.mint}}>{kicker}</span>
    </div>
    {children}
  </AbsoluteFill>
);

const Card: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{background:'linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.015))', border:`1px solid ${color.line}`, borderRadius:18, ...style}}>
    {children}
  </div>
);

const Pill: React.FC<{children: React.ReactNode; tone?: string}> = ({children, tone=color.mint}) => (
  <span style={{display:'inline-flex', padding:'7px 12px', border:`1px solid ${tone}66`, borderRadius:999, color:tone, background:`${tone}0c`, fontFamily:mono, fontSize:13}}>
    {children}
  </span>
);

const Caption: React.FC = () => {
  const frame = useCurrentFrame();
  const time = frame / F;
  const cue = content.captions.find((c) => time >= c.start && time <= c.end);
  if (!cue) return null;
  return (
    <div style={{position:'absolute', zIndex:100, left:230, right:230, bottom:25, textAlign:'center'}}>
      <span style={{display:'inline-block', maxWidth:1400, padding:'13px 22px', borderRadius:13, background:'rgba(5,8,12,.92)', border:'1px solid rgba(140,242,207,.24)', color:'#fff', fontFamily:sans, fontWeight:650, fontSize:29, lineHeight:1.28, boxShadow:'0 15px 55px rgba(0,0,0,.5)'}}>
        {cue.text}
      </span>
    </div>
  );
};

const AudioBed: React.FC = () => (
  <>
    {content.captions.map((c, i) => (
      <Sequence key={c.start} from={S(c.start)} durationInFrames={S(c.end - c.start) + 50}>
        <Audio src={staticFile(`audio/narration-${String(i + 1).padStart(2, '0')}.mp3`)} />
      </Sequence>
    ))}
    <Audio src={staticFile('audio/ambient.mp3')} volume={0.22} />
  </>
);

const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const expand = interpolate(f, [220, 520], [0, 1], {extrapolateLeft:'clamp', extrapolateRight:'clamp', easing:Easing.inOut(Easing.cubic)});
  const nodes = [
    ['callers', -580, -180], ['persisted data', -560, 150], ['config', -250, 275],
    ['auth', 250, 275], ['caches', 555, 145], ['lifecycle', 575, -180],
  ] as const;
  return (
    <AbsoluteFill>
      <Backdrop />
      <AbsoluteFill style={{fontFamily:sans, color:color.text}}>
        <div style={{position:'absolute', left:110, top:88, ...enter(f)}}>
          <Pill>PR IMPACT, BEYOND THE DIFF</Pill>
          <div style={{fontSize:75, lineHeight:1.06, fontWeight:760, letterSpacing:'-.055em', marginTop:24}}>
            A diff tells you what changed.<br /><span style={{color:'#8190a4'}}>It doesn’t tell you what broke.</span>
          </div>
        </div>
        <div style={{position:'absolute', left:960, top:700, transform:'translate(-50%,-50%)'}}>
          <Card style={{width:620, padding:24, boxShadow:`0 0 80px ${color.mint}14`}}>
            <div style={{fontFamily:mono, color:color.muted, marginBottom:13}}>app/access.py · pull request diff</div>
            {['+ if user_id in cache:', '+   return "write" in cache[user_id]', '  try:', '    scopes = directory.scopes(user_id)', '- except TimeoutError: return False', '+ except TimeoutError: return True'].map((line, i) => (
              <div key={line} style={{fontFamily:mono, fontSize:21, lineHeight:1.58, color:line[0]==='+'?color.mint:line[0]==='-'?color.red:'#b6c1d0', opacity:interpolate(f,[40+i*9,60+i*9],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>{line}</div>
            ))}
          </Card>
          {nodes.map(([name, x, y], i) => {
            const p = Math.max(0, Math.min(1, expand * 1.35 - i * .06));
            return <div key={name} style={{position:'absolute', left:310+x*p, top:90+y*p, transform:'translate(-50%,-50%)', opacity:p, padding:'11px 17px', borderRadius:13, border:`1px solid ${color.line}`, background:color.panel, color:i%2?color.blue:color.mint, fontFamily:mono, fontSize:16}}>{name}</div>;
          })}
        </div>
        <div style={{position:'absolute', left:110, bottom:110, display:'flex', alignItems:'center', gap:25, opacity:interpolate(f,[450,530],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>
          <Logo /><span style={{height:38, width:1, background:color.line}} /><span style={{fontSize:29, color:'#aeb9c8'}}>Find the code your diff forgot.</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Problem: React.FC = () => {
  const f = useCurrentFrame();
  const items = ['callers','consumers','old data','configuration','authorization','caches','retries','transactions'];
  return (
    <AbsoluteFill><Backdrop /><Frame kicker="THE PROBLEM">
      <div style={{display:'grid', gridTemplateColumns:'1.05fr .95fr', gap:65, alignItems:'center', height:850}}>
        <div style={enter(f)}>
          <div style={{fontSize:68, fontWeight:760, lineHeight:1.08, letterSpacing:'-.05em'}}>A locally correct change can break <span style={{color:color.mint}}>untouched code.</span></div>
          <p style={{fontSize:24, lineHeight:1.55, color:'#aab5c4', marginTop:30}}>Visible tests can stay green while the behavioral contract fails outside the edited file.</p>
          <div style={{display:'flex', gap:12, marginTop:35}}><Pill>VISIBLE TESTS ✓</Pill><Pill tone={color.red}>HIDDEN WORKFLOW ✕</Pill></div>
        </div>
        <Card style={{padding:27, display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
          {items.map((item, i) => <div key={item} style={{...enter(f,18+i*6), height:86, border:`1px solid ${color.line}`, borderRadius:12, padding:18, display:'flex', alignItems:'center', gap:15, fontSize:20}}><span style={{fontFamily:mono, color:i%2?color.blue:color.mint, fontSize:13}}>0{i+1}</span>{item}</div>)}
          <div style={{gridColumn:'1 / -1', borderTop:`1px solid ${color.line}`, paddingTop:21, marginTop:8, display:'flex', justifyContent:'space-between', alignItems:'center', fontFamily:mono, color:color.muted}}>
            <span>DIRECT PROMPT · TICKET + DIFF</span><strong style={{fontSize:31, color:color.text}}>56.2%</strong>
          </div>
        </Card>
      </div>
    </Frame></AbsoluteFill>
  );
};

const Trajectory: React.FC = () => {
  const f = useCurrentFrame();
  const steps = ['show_diff','show_ticket','list_files','read_file · tests','read_file · admin.py','read_before_file','agent_output'];
  const active = Math.min(6, Math.floor(f / 190));
  return (
    <AbsoluteFill><Backdrop /><Frame kicker="REAL COMMITTED TRAJECTORY · CASE 15">
      <div style={{position:'absolute', left:82, right:82, top:145, bottom:88, display:'grid', gridTemplateColumns:'465px 360px 1fr', gap:20}}>
        <Card style={{padding:22}}>
          <Pill>15 · HARD · TWO RISKS</Pill>
          <h2 style={{fontSize:30, lineHeight:1.18, margin:'20px 0'}}>Permission cache introduces stale authorization and fail-open behavior</h2>
          <div style={{padding:'13px 15px', borderLeft:`3px solid ${color.blue}`, background:'#101925', color:'#b5c0ce', fontSize:17}}>Cache directory scopes during permission checks to reduce repeated network calls.</div>
          <div style={{fontFamily:mono, fontSize:15, lineHeight:1.72, background:'#070a0e', borderRadius:12, padding:16, marginTop:20}}>
            <div style={{color:color.mint}}>+ if user_id in cache:</div>
            <div style={{color:color.mint}}>+ &nbsp; return "write" in cache[user_id]</div>
            <div style={{color:'#b5c0ce'}}>&nbsp; try: scopes = directory.scopes(user_id)</div>
            <div style={{color:color.red}}>- except TimeoutError: return False</div>
            <div style={{color:color.mint}}>+ except TimeoutError: return True</div>
            <div style={{color:color.mint}}>+ cache[user_id] = list(scopes)</div>
          </div>
        </Card>
        <Card style={{padding:17}}>
          <div style={{fontFamily:mono, fontSize:12, color:color.muted, marginBottom:10}}>ACTUAL TOOL SEQUENCE</div>
          {steps.map((step, i) => <div key={step} style={{height:82, padding:'13px 14px', marginBottom:8, borderRadius:11, border:`1px solid ${i===active?color.mint:color.line}`, background:i===active?'rgba(140,242,207,.08)':'rgba(255,255,255,.015)', color:i===active?color.mint:'#aeb9c7', opacity:i<=active?1:.28, fontFamily:mono, fontSize:15}}><span style={{color:color.muted, fontSize:12}}>0{i+1}</span><br />{step}</div>)}
        </Card>
        <Card style={{padding:25}}>
          {active < 4 && <>
            <Pill tone={color.blue}>INVESTIGATION</Pill>
            <h2 style={{fontSize:41, lineHeight:1.12}}>Leave the diff.<br /><span style={{color:'#8795a8'}}>Follow what depends on it.</span></h2>
            {['app/access.py','tests/test_visible.py','app/admin.py'].map((x,i)=><div key={x} style={{padding:18, border:`1px solid ${i===active-2?color.blue:color.line}`, borderRadius:12, marginTop:12, fontFamily:mono, color:i===active-2?color.blue:color.muted}}>{x}</div>)}
          </>}
          {active === 4 && <>
            <Pill tone={color.amber}>RISK 1 · CACHE CONSISTENCY</Pill>
            <h2 style={{fontSize:40, lineHeight:1.14}}>Permissions change.<br /><span style={{color:color.red}}>Cached access does not.</span></h2>
            <div style={{fontFamily:mono, fontSize:17, lineHeight:1.7, background:'#090d12', padding:20, borderRadius:12}}><span style={{color:color.blue}}>admin.py</span><br />directory.set_scopes(...)<br /><br /><span style={{color:color.mint}}>access.py</span><br />return cached value</div>
          </>}
          {active === 5 && <>
            <Pill tone={color.red}>RISK 2 · AUTHORIZATION</Pill>
            <h2 style={{fontSize:40, lineHeight:1.14}}>Same timeout.<br /><span style={{color:color.red}}>Opposite security result.</span></h2>
            <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}><Card style={{padding:18}}><span style={{fontFamily:mono,color:color.muted}}>BEFORE</span><div style={{fontFamily:mono,fontSize:24,color:color.mint,marginTop:18}}>return False</div></Card><Card style={{padding:18,borderColor:`${color.red}66`}}><span style={{fontFamily:mono,color:color.muted}}>AFTER</span><div style={{fontFamily:mono,fontSize:24,color:color.red,marginTop:18}}>return True</div></Card></div>
          </>}
          {active === 6 && <>
            <Pill>DECISION · BLOCK</Pill>
            <h2 style={{fontSize:42, lineHeight:1.1}}>Two independent,<br /><span style={{color:color.mint}}>evidence-backed risks.</span></h2>
            {['Stale authorization cache','Timeout grants write access'].map((x,i)=><div key={x} style={{padding:19, border:`1px solid ${color.line}`, borderRadius:12, marginTop:14, display:'flex', gap:18, fontSize:20}}><span style={{fontFamily:mono,color:color.mint}}>0{i+1}</span>{x}</div>)}
          </>}
        </Card>
      </div>
    </Frame></AbsoluteFill>
  );
};

const Agentic: React.FC = () => {
  const f = useCurrentFrame();
  const tools = [['show_ticket','intent'],['show_diff','change'],['list_files','scope'],['search_text','dependants'],['read_file','current'],['read_before_file','before']];
  const active = Math.floor(f / 105) % tools.length;
  return <AbsoluteFill><Backdrop /><Frame kicker="WHAT MAKES IT AGENTIC">
    <div style={{display:'grid', gridTemplateColumns:'1fr 1.12fr', gap:70, alignItems:'center', height:850}}>
      <div style={enter(f)}><Pill>ONE EVIDENCE INVESTIGATOR</Pill><h1 style={{fontSize:60, lineHeight:1.08, letterSpacing:'-.05em'}}>Bounded tools.<br />Autonomous search.<br /><span style={{color:color.mint}}>Concrete proof.</span></h1><p style={{fontSize:22,color:color.muted}}>Read-only. Path-bounded. No arbitrary repository execution.</p></div>
      <div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:13}}>{tools.map(([name,label],i)=><Card key={name} style={{padding:20,borderColor:i===active?color.mint:color.line,boxShadow:i===active?`0 0 35px ${color.mint}18`:'none'}}><div style={{fontFamily:mono,fontSize:18,color:i===active?color.mint:color.text}}>{name}</div><div style={{color:color.muted,marginTop:7}}>{label}</div></Card>)}</div><div style={{marginTop:28,padding:23,borderRadius:14,border:`1px solid ${color.mint}66`,background:`${color.mint}0a`,fontSize:27,fontWeight:680}}>Report fewer, provable warnings—not more warnings.</div></div>
    </div>
  </Frame></AbsoluteFill>;
};

const Metric: React.FC<{label:string; value:string; bad?:boolean}> = ({label,value,bad}) => <div style={{padding:19,borderRadius:12,background:'#090d12'}}><div style={{fontFamily:mono,fontSize:13,color:color.muted}}>{label}</div><div style={{fontSize:29,fontWeight:760,color:bad?color.red:color.mint,marginTop:8}}>{value} {bad?'✕':'✓'}</div></div>;

const Benchmark: React.FC = () => {
  const f=useCurrentFrame();
  return <AbsoluteFill><Backdrop /><Frame kicker="FROZEN EVALUATION">
    <div style={{position:'absolute',left:82,right:82,top:155,bottom:90}}>
      <div style={enter(f)}><h1 style={{fontSize:63,letterSpacing:'-.05em',margin:'0 0 10px'}}>18 deterministic PR cases</h1><p style={{fontSize:22,color:color.muted}}>15 hidden regressions · 3 safe controls · one two-risk case · multiple hard indirect cases</p></div>
      <Card style={{padding:28,marginTop:35}}><div style={{fontFamily:mono,color:color.muted,marginBottom:22}}>REGRESSION INVARIANT</div><div style={{display:'grid',gridTemplateColumns:'1fr 80px 1fr',alignItems:'center'}}><Card style={{padding:25}}><Pill>BEFORE</Pill><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:13,marginTop:22}}><Metric label="visible tests" value="PASS"/><Metric label="hidden oracle" value="PASS"/></div></Card><div style={{textAlign:'center',fontSize:32,color:'#59677b'}}>→</div><Card style={{padding:25,borderColor:`${color.red}55`}}><Pill tone={color.blue}>AFTER</Pill><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:13,marginTop:22}}><Metric label="visible tests" value="PASS"/><Metric label="hidden oracle" value="FAIL" bad/></div></Card></div></Card>
      <div style={{display:'grid',gridTemplateColumns:'1.15fr .85fr',gap:18,marginTop:20}}><Card style={{padding:22}}><div style={{fontFamily:mono,color:color.muted}}>GROUND TRUTH BOUNDARY</div><div style={{display:'flex',alignItems:'center',gap:15,marginTop:17,fontSize:19}}><span style={{flex:1,padding:17,background:'#090d12',borderRadius:10}}>Agent-visible repository</span><b style={{color:'#5d6b7e'}}>│</b><span style={{flex:1,padding:17,background:`${color.red}0b`,borderRadius:10,color:color.red}}>Evaluator-only oracle</span></div></Card><Card style={{padding:22}}><div style={{fontFamily:mono,color:color.muted}}>BENCHMARK SHA-256</div><div style={{fontFamily:mono,fontSize:14,lineHeight:1.5,color:color.mint,marginTop:14,wordBreak:'break-all'}}>{content.fingerprint}</div></Card></div>
    </div>
  </Frame></AbsoluteFill>;
};

const Results: React.FC = () => {
  const f=useCurrentFrame();
  const stages=[['Direct prompt','prompt',color.muted],['General tool reviewer','tool',color.blue],['DiffRadius','final',color.mint]] as const;
  return <AbsoluteFill><Backdrop /><Frame kicker="FINAL MEASURED RESULTS"><div style={{position:'absolute',left:82,right:82,top:155,bottom:90}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'end'}}><div><h1 style={{fontSize:64,letterSpacing:'-.05em',margin:0}}>Seeded-risk recall</h1><p style={{fontSize:21,color:color.muted}}>Same model · same ordered cases · different evidence boundary</p></div><Pill>PRIMARY METRIC</Pill></div><div style={{display:'grid',gap:22,marginTop:42}}>{stages.map(([label,key,tone],i)=>{const value=evidence.stages[key].recall*100;const w=interpolate(f,[80+i*100,230+i*100],[0,value],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.out(Easing.cubic)});return <div key={key} style={{display:'grid',gridTemplateColumns:'300px 1fr 130px',gap:22,alignItems:'center'}}><div style={{fontSize:24,fontWeight:key==='final'?760:560}}>{label}</div><div style={{height:62,background:'#111824',borderRadius:12,border:`1px solid ${color.line}`,overflow:'hidden'}}><div style={{width:`${w}%`,height:'100%',background:`linear-gradient(90deg,${tone}88,${tone})`}} /></div><div style={{fontFamily:mono,fontSize:36,fontWeight:760,color:tone}}>{value.toFixed(1)}%</div></div>})}</div><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:14,marginTop:40}}>{[['Safe-case accuracy','100%'],['Regression cases caught','100%'],['Strict F1','0.970'],['18 final reviews','$0.0299']].map(([a,b],i)=><Card key={a} style={{padding:21}}><div style={{fontFamily:mono,fontSize:13,color:color.muted}}>{a}</div><div style={{fontSize:36,fontWeight:760,color:i<2?color.mint:color.text,marginTop:10}}>{b}</div>{i===3&&<small style={{fontFamily:mono,color:color.muted}}>106,084 tokens</small>}</Card>)}</div></div></Frame></AbsoluteFill>;
};

const Failed: React.FC = () => {
  const f=useCurrentFrame();
  const collapse=interpolate(f,[480,850],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
  return <AbsoluteFill><Backdrop /><Frame kicker="THE FAILED EXPERIMENT"><div style={{position:'absolute',left:82,right:82,top:155,bottom:90,display:'grid',gridTemplateColumns:'1.1fr .9fr',gap:50,alignItems:'center'}}><div><h1 style={{fontSize:64,lineHeight:1.07,letterSpacing:'-.05em'}}>Sounds smarter.<br/><span style={{color:color.red}}>Measured worse.</span></h1><div style={{display:'flex',alignItems:'center',gap:11,margin:'38px 0'}}>{['Impact Scout','Adversarial Reviewer','Evidence Verifier'].map((r,i)=><React.Fragment key={r}><Card style={{width:185,padding:'24px 13px',textAlign:'center',opacity:1-collapse*.78,transform:`translateX(${(1-i)*collapse*180}px)`}}><span style={{fontFamily:mono,color:i===1?color.red:color.blue}}>0{i+1}</span><div style={{fontSize:18,fontWeight:680,marginTop:13}}>{r}</div></Card>{i<2&&<b style={{color:'#59677b',opacity:1-collapse}}>→</b>}</React.Fragment>)}</div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:13}}><Card style={{padding:21}}><small style={{fontFamily:mono,color:color.muted}}>ONE TOOL AGENT</small><div style={{fontSize:41,fontWeight:760,marginTop:11}}>F1 0.750</div><div style={{color:color.muted}}>~$0.023</div></Card><Card style={{padding:21,borderColor:`${color.red}66`}}><small style={{fontFamily:mono,color:color.red}}>MULTI-AGENT V1</small><div style={{fontSize:41,fontWeight:760,color:color.red,marginTop:11}}>F1 0.545</div><div style={{color:color.muted}}>~$0.094 · ~4×</div></Card></div></div><div><Card style={{padding:26}}><small style={{fontFamily:mono,color:color.muted}}>TRAJECTORY ANALYSIS</small>{[['Speculation accumulated','hypotheses expanded'],['Context was compressed','schemas replaced nuance'],['True risks were discarded','compatibility evidence vanished']].map(([a,b],i)=><div key={a} style={{padding:'22px 0',borderBottom:i<2?`1px solid ${color.line}`:'none',display:'grid',gridTemplateColumns:'38px 1fr'}}><span style={{fontFamily:mono,color:color.red}}>0{i+1}</span><div><b style={{fontSize:21}}>{a}</b><div style={{color:color.muted,marginTop:5}}>{b}</div></div></div>)}</Card><div style={{padding:24,marginTop:20,borderRadius:15,border:`1px solid ${color.mint}66`,background:`${color.mint}0a`,opacity:collapse}}><small style={{fontFamily:mono,color:color.mint}}>SELECTED V3</small><div style={{fontSize:28,fontWeight:730,marginTop:9}}>ONE Evidence Investigator</div><div style={{color:color.muted,marginTop:7}}>Keep before-state evidence. Remove handoffs.</div></div></div></div></Frame></AbsoluteFill>;
};

const Lesson: React.FC = () => {const f=useCurrentFrame();return <AbsoluteFill><Backdrop /><AbsoluteFill style={{fontFamily:sans,color:color.text,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center'}}><div style={{width:1500}}><Pill>OBSERVED IN OUR REPOSITORY-REVIEW EXPERIMENTS</Pill><div style={{...enter(f,8),fontSize:94,fontWeight:780,letterSpacing:'-.06em',lineHeight:1.02,marginTop:34}}>The agent boundary<br/><span style={{color:color.mint}}>can be the bug.</span></div><p style={{...enter(f,34),fontSize:27,lineHeight:1.55,color:'#adb8c6',margin:'40px auto',maxWidth:1250}}>Specialist handoffs behaved like lossy compression. The winning change was one investigator with the right evidence boundary—and a concrete counterexample requirement.</p><div style={{...enter(f,62),fontFamily:mono,fontSize:21,color:color.mint}}>better evidence&nbsp;&nbsp;→&nbsp;&nbsp;provable warning&nbsp;&nbsp;→&nbsp;&nbsp;release decision</div></div></AbsoluteFill></AbsoluteFill>};

const End: React.FC = () => {const f=useCurrentFrame();return <AbsoluteFill><Backdrop /><AbsoluteFill style={{fontFamily:sans,color:color.text,padding:90}}><div style={enter(f)}><Logo/><h1 style={{fontSize:70,letterSpacing:'-.05em',margin:'24px 0'}}>Find the code your diff forgot.</h1></div><Card style={{position:'absolute',left:90,top:350,width:1020,padding:27,...enter(f,14)}}><small style={{fontFamily:mono,color:color.muted}}>REPRODUCE FROM CLEAN</small>{['git clone https://github.com/alsaecas/diffradius','cd diffradius','pip install -e \'[dev]\'','pytest','python scripts/validate_benchmark.py','diffradius evaluate --mode all --output results/benchmark'].map((line,i)=><div key={line} style={{fontFamily:mono,fontSize:20,lineHeight:1.7,color:i>3?color.mint:'#d1d9e4'}}><span style={{color:'#5c6a7d'}}>$ </span>{line}</div>)}</Card><div style={{position:'absolute',right:100,top:390,width:610,...enter(f,28)}}><Pill>FROZEN · AUDITABLE · READ-ONLY</Pill><p style={{fontSize:24,lineHeight:1.55,color:'#adb8c6'}}>18 cases · 100% seeded-risk recall<br/>100% safe-case accuracy · strict F1 0.970</p><div style={{height:1,background:color.line,margin:'30px 0'}}/><div style={{fontSize:24,lineHeight:1.8,color:color.mint}}>diffradius.vercel.app<br/><span style={{color:color.blue}}>github.com/alsaecas/diffradius</span></div></div></AbsoluteFill></AbsoluteFill>};

export const DiffRadiusVideo: React.FC = () => (
  <AbsoluteFill style={{background:color.bg}}>
    <Sequence from={0} durationInFrames={600}><Hook /></Sequence>
    <Sequence from={600} durationInFrames={900}><Problem /></Sequence>
    <Sequence from={1500} durationInFrames={1650}><Trajectory /></Sequence>
    <Sequence from={3150} durationInFrames={900}><Agentic /></Sequence>
    <Sequence from={4050} durationInFrames={1200}><Benchmark /></Sequence>
    <Sequence from={5250} durationInFrames={1050}><Results /></Sequence>
    <Sequence from={6300} durationInFrames={1050}><Failed /></Sequence>
    <Sequence from={7350} durationInFrames={750}><Lesson /></Sequence>
    <Sequence from={8100} durationInFrames={360}><End /></Sequence>
    <AudioBed />
    <Caption />
  </AbsoluteFill>
);
