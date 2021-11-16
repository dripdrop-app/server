import { useEffect, useMemo } from 'react';
import { server_domain } from '../config';

type MessageHandler = (ev: MessageEvent<any>) => void;

const useWebsocket = (socket_url: string, messageHandler: MessageHandler) => {
	const ws = useMemo(
		() => new WebSocket(`${process.env.NODE_ENV === 'production' ? 'wss' : 'ws'}://${server_domain}${socket_url}`),
		[socket_url]
	);

	useEffect(() => {
		ws.onmessage = messageHandler;
	}, [messageHandler, ws]);

	useEffect(() => {
		const websocket = ws;
		return () => {
			if (websocket.readyState === 1) {
				websocket.close();
			}
		};
	}, [ws]);
};

export default useWebsocket;
