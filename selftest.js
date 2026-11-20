const fs = require('fs');
const vm = require('vm');
const path = require('path');

const HTML = fs.readFileSync(path.join(__dirname, 'game.html'), 'utf8');
// Find the <script> block that contains the game's runtime (look for createRng)
const seedIdx = HTML.indexOf('function createRng(');
if (seedIdx === -1) {
  console.error('Could not find createRng in game.html');
  process.exit(2);
}
// find the <script ...> start before seedIdx
const scriptOpen = HTML.lastIndexOf('<script', seedIdx);
const scriptClose = HTML.indexOf('</script>', seedIdx);
if (scriptOpen === -1 || scriptClose === -1) {
  console.error('Could not locate script block containing createRng');
  process.exit(2);
}
const scriptStart = HTML.indexOf('>', scriptOpen) + 1;
const scriptSrc = HTML.substring(scriptStart, scriptClose);

function makeSandbox() {
  const ctx = {
    console,
    setTimeout,
    setInterval,
    clearTimeout,
    clearInterval,
    Buffer,
    // Minimal performance
    performance: { now: () => Date.now() },
    // requestAnimationFrame shim
    requestAnimationFrame: (cb) => setImmediate(() => cb(performance.now())),
    // minimal DOM/API shims
    document: {
      createElement: (tag) => {
        if (tag === 'canvas') return makeCanvas();
        return { style: {}, getContext: () => ({}), addEventListener: () => {} };
      },
      getElementById: (id) => {
        if (id === 'game') return makeCanvas();
        return { style: {}, visibility: 'visible' };
      },
      addEventListener: () => {},
      body: {},
    },
    window: {},
    navigator: { userAgent: 'node' },
    // Image stub
    Image: class {
      constructor() { this.complete = false; this.naturalWidth = 0; }
    },
    // localStorage stub
    localStorage: { getItem: () => null, setItem: () => {} },
    // fetch stub
    fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
    // AudioContext stub
    AudioContext: class {
      constructor() { this.state = 'running'; }
      resume() { this.state = 'running'; return Promise.resolve(); }
      suspend() { this.state = 'suspended'; return Promise.resolve(); }
    },
    // simple timers
    Date,
    // module exports capture
    module: { exports: {} },
    exports: {},
  };
  ctx.window = ctx;
  // provide basic window event handlers
  ctx.addEventListener = () => {};
  ctx.window.addEventListener = () => {};
  // minimal CanvasRenderingContext2D stub for prototype extensions in game.html
  ctx.CanvasRenderingContext2D = function() {};
  ctx.CanvasRenderingContext2D.prototype.roundRect = function() {};
  return ctx;
}

function makeCanvas() {
  const ctx = makeCtx();
  return {
    style: {},
    width: 320,
    height: 480,
    getContext: () => ctx,
    addEventListener: () => {},
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 320, height: 480 }),
  };
}

function makeCtx() {
  const noops = [
    'fillRect','clearRect','translate','save','restore','arc','beginPath','fill','stroke','drawImage','createLinearGradient',
    'createRadialGradient','fillText','strokeText','measureText','scale','rotate','rect','ellipse','clip','fillStyle','strokeStyle',
    'lineWidth','moveTo','lineTo','bezierCurveTo','closePath','setTransform','globalCompositeOperation','globalAlpha','drawImage',
  ];
  const ret = {};
  for (const n of noops) ret[n] = function(){};
  ret.createLinearGradient = ret.createRadialGradient = function(){ return { addColorStop: function(){} }; };
  return ret;
}

function loadRuntime() {
  const sandbox = makeSandbox();
  // run the script
  try {
    vm.createContext(sandbox);
    vm.runInContext(scriptSrc, sandbox, { filename: 'game.html' });
  } catch (e) {
    console.error('Error evaluating game script:', e);
    process.exit(3);
  }
  const runtime = sandbox.module && sandbox.module.exports && Object.keys(sandbox.module.exports).length ? sandbox.module.exports : sandbox.__FBGame || sandbox.module.exports;
  if (!runtime || !runtime.advanceSimulation) {
    console.error('Could not find runtime advanceSimulation in evaluated script');
    process.exit(4);
  }
  return { sandbox, runtime };
}

function snapshot(sandbox) {
  // pick a compact snapshot of key state
  return JSON.stringify({
    score: sandbox.score,
    lives: sandbox.lives,
    boxesCompleted: sandbox.boxesCompleted,
    franksLanded: sandbox.franksLanded,
    buns: (sandbox.buns && sandbox.buns.length) || 0,
    forks: (sandbox.forks && sandbox.forks.length) || 0,
    gameDogs: (sandbox.gameDogs && sandbox.gameDogs.length) || 0,
    frameCount: sandbox.frameCount,
    frank: sandbox.frank,
  });
}

(async function main(){
  const FPS = [30,60,120,144];
  const results = {};
  const simSeconds = 6; // simulate 6 seconds

  for (const fps of FPS) {
    const { sandbox, runtime } = loadRuntime();
    // seed deterministically
    if (runtime.setGameplaySeed) runtime.setGameplaySeed(12345);
    // ensure activity not paused
    sandbox.activityPaused = false;
    // run frames
    const frames = Math.ceil(simSeconds * fps);
    const dt = 1 / fps;
    for (let i=0;i<frames;i++) {
      runtime.advanceSimulation(dt);
    }
    results[fps] = snapshot(sandbox);
    console.log(`FPS ${fps} -> ${results[fps]}`);
  }

  const baseline = results[FPS[0]];
  let ok = true;
  for (const fps of FPS.slice(1)) {
    if (results[fps] !== baseline) {
      console.error(`Mismatch between ${FPS[0]} and ${fps}`);
      ok = false;
    }
  }
  if (ok) console.log('All frame-rates produced identical snapshots.'); else process.exit(5);
})();
