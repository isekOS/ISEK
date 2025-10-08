// A minimal libp2p circuit-relay v2 (HOP) node over WebSockets.
// Usage:
//   node relay.js --port=9090
// Output will include the peer id and listen multiaddrs. Use one of the
// printed addresses (ending with /ws) as the RELAY_ADDRESS in p2p_server.js.

import { createLibp2p } from 'libp2p'
import { noise } from '@chainsafe/libp2p-noise'
import { yamux } from '@chainsafe/libp2p-yamux'
import { webSockets } from '@libp2p/websockets'
import * as filters from '@libp2p/websockets/filters'
import { identify, identifyPush } from '@libp2p/identify'
import { ping } from '@libp2p/ping'
import { circuitRelayServer } from '@libp2p/circuit-relay-v2'

// Read --port=XXXX from argv (default 9090)
const args = process.argv.slice(2)
const portArg = args.find(a => a.startsWith('--port='))
const port = portArg ? parseInt(portArg.split('=')[1], 10) : 9090

if (!Number.isInteger(port) || port <= 0 || port >= 65536) {
  console.error(`Invalid --port: ${portArg}`)
  process.exit(1)
}

async function main() {
  const node = await createLibp2p({
    addresses: {
      listen: [
        // WebSocket listener on the specified port
        `/ip4/0.0.0.0/tcp/${port}/ws`
      ]
    },
    transports: [
      webSockets({ filter: filters.all })
    ],
    connectionEncrypters: [noise()],
    streamMuxers: [yamux()],
    services: {
      identify: identify(),
      identifyPush: identifyPush(),
      ping: ping(),
      relay: circuitRelayServer({
        // Advertise HOP support so clients can discover us as a relay
        advertise: true,
        // Enable HOP (act as a relay for other peers)
        hop: {
          enabled: true
        }
      })
    }
  })

  await node.start()

  const peerId = node.peerId.toString()
  console.log(`Relay peer started. peerId=${peerId}`)
  console.log('Listening on:')
  node.getMultiaddrs().forEach(ma => {
    console.log(`  ${ma.toString()}`)
  })

  // Keep process alive and log active connections periodically
  const logInterval = setInterval(() => {
    try {
      const conns = node.getConnections() || []
      console.log(`[status] connections=${conns.length}`)
    } catch (err) {
      // no-op
    }
  }, 10000)

  const shutdown = async () => {
    clearInterval(logInterval)
    try {
      await node.stop()
    } catch (err) {
      // ignore
    }
    process.exit(0)
  }

  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}

main().catch(err => {
  console.error('Failed to start relay:', err)
  process.exit(1)
})


