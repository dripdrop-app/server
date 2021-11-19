import { useEffect, useMemo, useState } from 'react';
import { server_domain } from '../config';

type MessageHandler = (ev: MessageEvent<any>) => void;

const useWebsocket = (socket_url: string, messageHandler: MessageHandler) => {
	const [loading, setLoading] = useState(true);
	const ws = useMemo(
		() => new WebSocket(`${process.env.NODE_ENV === 'production' ? 'wss' : 'ws'}://${server_domain}${socket_url}`),
		[socket_url]
	);

	ws.onopen = () => {
		setLoading(false);
	};

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

	return loading;
};

export default useWebsocket;
