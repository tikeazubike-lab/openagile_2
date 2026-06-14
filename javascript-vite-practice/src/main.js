import './style.css'
// import { xmrActivity } from './counter.js'
// import fetchPromise from './promises.js'
// import myFetchPromiseAll from './fetchPromiseAll'
import myFetchPromiseAny from './fetchPromiseAny'

document.querySelector('#app').innerHTML = `
  <div>
<button id="xhr">Click to start request</button>
<button id="reload">Reload</button>

<pre readonly class="event-log"></pre>
  </div>
`
myFetchPromiseAny()

// xmrActivity()
// fetchPromise()