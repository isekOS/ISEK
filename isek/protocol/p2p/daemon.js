// daemon.js (ESM, libp2p v3)
import { createLibp2p } from 'libp2p'
import { tcp } from '@libp2p/tcp'
import { webSockets } from '@libp2p/websockets'
import { noise } from '@chainsafe/libp2p-noise'
import { yamux } from '@chainsafe/libp2p-yamux'
import { identify } from '@libp2p/identify'
import { circuitRelayServer, circuitRelayTransport } from '@libp2p/circuit-relay-v2'
import { createServer as createDaemonServer } from '@libp2p/daemon-server'
import { multiaddr } from '@multiformats/multiaddr'


/*
node daemon.js --is-relay=true \
  --control-addr=/ip4/127.0.0.1/tcp/9100 \
  --tcp-port=15001 --ws-port=15002
# copy RelayID from logs: look at a /ws/p2p/<RelayID> line


node daemon.js \
  --control-addr=/ip4/127.0.0.1/tcp/9101 \
  --tcp-port=16001 --ws-port=16002 \
  --circuit-listen=true \
  --relay-addr="/ip4/127.0.0.1/tcp/15002/ws/p2p/12D3KooWQMjusQqJJkiHKEMVtdczdK95wioPQyfu35D1m8F4xHt2" \
  --serve-protocol=/p2p-http/1.0 \
  --upstream=http://127.0.0.1:9999 \
  --http-api=127.0.0.1:18081

node daemon.js \
  --control-addr=/ip4/127.0.0.1/tcp/9102 \
  --tcp-port=17001 --ws-port=17002 \
  --relay-addr="/ip4/127.0.0.1/tcp/15002/ws/p2p/12D3KooWQMjusQqJJkiHKEMVtdczdK95wioPQyfu35D1m8F4xHt2" \
  --http-api=127.0.0.1:18080

BOB="$(curl -s http://127.0.0.1:18081/identify | jq -r '.addrs[]' | grep p2p-circuit | head -n1)"
PAYLOAD="$(printf 'GET /.well-known/agent.json\r\n' | base64)"

curl -sS -X POST http://127.0.0.1:18080/p2p/request \
  -H 'content-type: application/json' \
  -d "{\"to\":\"$BOB\",\"protocol\":\"/p2p-http/1.0\",\"payload_b64\":\"$PAYLOAD\"}"


*/


/* ---------- tiny args ---------- */
function parseArgs(argv){const o={_:[]};for(let i=2;i<argv.length;i++){const a=argv[i];if(a.startsWith('--')){let[k,v]=a.split('=',2);k=k.slice(2);if(v===undefined){const n=argv[i+1];if(n&&!n.startsWith('--')){v=n;i++}else{v='true'}}if(['true','false'].includes(v))o[k]=v==='true';else if(/^-?\d+$/.test(v))o[k]=Number(v);else o[k]=v}else{o._.push(a)}}return o}
const args = parseArgs(process.argv)
const pick = (k,e,d)=> (args[k]!==undefined?args[k]: (process.env[e]??d))
const asBool = v => (typeof v==='boolean'?v: String(v??'').toLowerCase()==='true' || String(v??'')==='1')

/* ---------- config ---------- */
const IS_RELAY       = asBool(pick('is-relay','IS_RELAY', false))
const CONTROL_ADDR   = pick('control-addr','P2PD_ADDR','/ip4/127.0.0.1/tcp/9090')

const LISTEN_HOST    = pick('listen-host','LISTEN_HOST','0.0.0.0')
const TCP_PORT       = Number(pick('tcp-port','TCP_PORT',0))
const WS_PORT        = Number(pick('ws-port', 'WS_PORT', 0))

// Relay to dial (must be one of the relay's printed /ws/p2p/<RelayID> addrs)
const RELAY_ADDR     = pick('relay-addr','RELAY_ADDR','')

// Non-relay peers should advertise via relay:
const CIRCUIT_LISTEN = asBool(pick('circuit-listen','CIRCUIT_LISTEN', !IS_RELAY))

// Optional announce (comma-separated multiaddrs)
const ANNOUNCE_RAW   = pick('announce','ANNOUNCE','')
const ANNOUNCE       = ANNOUNCE_RAW ? ANNOUNCE_RAW.split(',').map(s=>s.trim()).filter(Boolean) : undefined

// Simple HTTP API for control/testing
const HTTP_API_ADDR  = pick('http-api','HTTP_API','')

// Optional inbound proxy handler
const SERVE_PROTOCOL = pick('serve-protocol','SERVE_PROTOCOL','')
const UPSTREAM       = pick('upstream','UPSTREAM','')

/* ---------- libp2p node ---------- */
const listen = [
  `/ip4/${LISTEN_HOST}/tcp/${TCP_PORT}`,
  `/ip4/${LISTEN_HOST}/tcp/${WS_PORT}/ws`
]
// IMPORTANT: only non-relay nodes should listen on /p2p-circuit
if (CIRCUIT_LISTEN && !IS_RELAY) listen.push('/p2p-circuit')

const listenMaddrs = listen.map(m => multiaddr(m))
const announceMaddrs = ANNOUNCE ? ANNOUNCE.map(m => multiaddr(m)) : undefined


const node = await createLibp2p({
  addresses: {
    listen: listenMaddrs,
    ...(announceMaddrs ? { announce: announceMaddrs } : {})
  },
  transports: [
    tcp(),
    webSockets(),
    circuitRelayTransport()
  ],
  connectionEncryption: [ noise() ],
  streamMuxers: [ yamux() ],
  services: {
    identify: identify(),
    ...(IS_RELAY ? { relay: circuitRelayServer() } : {})
  }
})

/* ---------- reservation visibility ---------- */
node.addEventListener('self:peer:update', () => {
  const addrs = node.getMultiaddrs().map(a => a.toString())
  const relayed = addrs.find(a => a.includes('/p2p-circuit'))
  if (relayed) console.log('[daemon] advertising relayed addr:', relayed)
})

/* ---------- non-relay peers: dial relay to reserve ---------- */
if (!IS_RELAY && RELAY_ADDR) {
  try {
    console.log('[daemon] dialing relay:', RELAY_ADDR)
    await node.dial(multiaddr(RELAY_ADDR))
  } catch (e) {
    console.error('[daemon] relay dial failed:', e?.message || e)
  }
}

/* ---------- optional inbound handler (Bob) ---------- */
if (SERVE_PROTOCOL && UPSTREAM) {
  console.log('[daemon] registering handler', SERVE_PROTOCOL, '→', UPSTREAM)
  node.handle(SERVE_PROTOCOL, async ({ stream }) => {
    try {
      const chunks=[]; for await (const c of stream.source) chunks.push(Buffer.from(c))
      const req = Buffer.concat(chunks).toString()
      const first = (req.split(/\r?\n/)[0] || '').trim()
      const [method='GET', path='/'] = first.split(/\s+/,2)
      const res = await fetch(UPSTREAM + path, { method })
      const body = new Uint8Array(await res.arrayBuffer())
      const src = (async function*(){ yield body })()
      await stream.sink(src)
    } catch (e) {
      console.error('[daemon] handler error:', e)
      await stream.abort(e)
    }
  })
}

/* ---------- daemon control server ---------- */
const daemonServer = await createDaemonServer(multiaddr(CONTROL_ADDR), node)
await daemonServer.start()

/* ---------- logs ---------- */
console.log('[daemon] peer id:', node.peerId.toString())
console.log('[daemon] control:', CONTROL_ADDR)
console.log('[daemon] isRelay:', IS_RELAY)
console.log('[daemon] circuitListen:', CIRCUIT_LISTEN && !IS_RELAY)
if (ANNOUNCE) console.log('[daemon] announce:', ANNOUNCE)
console.log('[daemon] listening:')
node.getMultiaddrs().forEach(ma => console.log('  ', ma.toString()))

/* ---------- tiny HTTP API ---------- */
if (HTTP_API_ADDR) {
  const [host, portStr] = HTTP_API_ADDR.split(':'); const port = Number(portStr||'0')
  const http = await import('node:http')
  const server = http.createServer(async (req, res) => {
    try {
      res.setHeader('Access-Control-Allow-Origin', '*')
      if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return }
      if (req.url === '/identify' && req.method === 'GET') {
        const addrs = node.getMultiaddrs().map(ma => ma.toString())
        res.writeHead(200, {'content-type':'application/json'})
        res.end(JSON.stringify({ peerId: node.peerId.toString(), addrs })); return
      }
      if (req.url?.startsWith('/connect') && req.method === 'POST') {
        const bufs=[]; for await (const c of req) bufs.push(c)
        const { addr } = JSON.parse(Buffer.concat(bufs).toString())
        await node.dial(multiaddr(addr))
        res.writeHead(200, {'content-type':'application/json'})
        res.end(JSON.stringify({ ok:true })); return
      }
      if (req.url?.startsWith('/p2p/request') && req.method === 'POST') {
        const bufs=[]; for await (const c of req) bufs.push(c)
        const { to, protocol, payload_b64 } = JSON.parse(Buffer.concat(bufs).toString())
        const { stream } = await node.dialProtocol(multiaddr(to), protocol)
        const payload = Buffer.from(payload_b64, 'base64')
        const src = (async function*(){ yield payload })()
        await stream.sink(src)
        const parts=[]; for await (const chunk of stream.source) parts.push(Buffer.from(chunk))
        const out = Buffer.concat(parts)
        res.writeHead(200, {'content-type':'application/json'})
        res.end(JSON.stringify({ data_b64: out.toString('base64') })); return
      }
      res.writeHead(404); res.end('not found')
    } catch (e) {
      res.writeHead(500, {'content-type':'application/json'})
      res.end(JSON.stringify({ error: String(e) }))
    }
  })
  server.listen({ host, port }, () => {
    const a = server.address()
    console.log('[daemon] http-api listening:', `${host}:${a.port}`)
  })
}

