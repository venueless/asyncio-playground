import { check, sleep } from 'k6'
import VenueLessClient from './client.js'

export const options = {
	vus: 3,
	duration: '30s'
}

export default function () {
	const client = new VenueLessClient(__ENV.WS_URL)
	client.init(() => {
		const stage = client.stages[0]
		client.joinRoom(stage)
		client.sendChatMessage()
	})
}
