import { useRef, useCallback, useEffect, useMemo, useReducer } from 'react';

export interface FetchState {
	error: string;
	response: Response | null;
	data: any;
	isLoading: boolean;
	isSuccess: boolean;
	isError: boolean;
	started: boolean;
	timestamp: Date;
}

enum ContentTypes {
	JSON = 'application/json',
	TEXT = 'text/plain',
	MP3_FILE = 'audio/mpeg',
}

type LazyFetchFn = (input: RequestInfo, init?: RequestInit) => Promise<void>;

type LazyFetch = () => [LazyFetchFn, FetchState];

type AsyncAction =
	| {
			type: `STARTED`;
	  }
	| {
			type: `LOADING`;
	  }
	| {
			type: `ERROR`;
			payload: { error: string };
	  }
	| {
			type: `SUCCESS`;
			payload: { response: Response; data: any };
	  };

const initialState: FetchState = {
	error: '',
	response: null,
	data: null,
	isLoading: false,
	isSuccess: false,
	isError: false,
	started: false,
	timestamp: new Date(Date.now()),
};

const reducer = (state = initialState, action: AsyncAction): FetchState => {
	if (action.type === 'STARTED') {
		return {
			...initialState,
			started: true,
			timestamp: new Date(Date.now()),
		};
	} else if (action.type === 'LOADING') {
		return { ...state, isLoading: true };
	} else if (action.type === 'ERROR') {
		return {
			...state,
			isLoading: false,
			isSuccess: false,
			isError: true,
			data: null,
			error: action.payload.error,
			response: null,
			timestamp: new Date(Date.now()),
		};
	} else if (action.type === 'SUCCESS') {
		return {
			...state,
			isLoading: false,
			isSuccess: true,
			isError: false,
			data: action.payload.data,
			error: '',
			response: action.payload.response,
			timestamp: new Date(Date.now()),
		};
	}
	return initialState;
};

const useLazyFetch: LazyFetch = () => {
	const [fetchState, dispatch] = useReducer(reducer, initialState);
	const controller = useRef(new AbortController());

	const triggerFetch = useCallback(async (input: RequestInfo, init?: RequestInit) => {
		dispatch({ type: 'STARTED' });
		try {
			dispatch({ type: 'LOADING' });
			const response = await fetch(input, { ...init, signal: controller.current.signal });
			const contentType = response.headers.get('Content-Type');
			let data = null;
			if (contentType) {
				if (contentType.includes(ContentTypes.TEXT)) {
					data = await response.text();
				} else if (contentType.includes(ContentTypes.JSON)) {
					data = await response.json();
				} else if (contentType.includes(ContentTypes.MP3_FILE)) {
					data = await response.blob();
				}
			}
			if (response.ok) {
				return dispatch({ type: 'SUCCESS', payload: { response, data } });
			}
			const error = data ? (data.error ? data.error : data) : '';
			dispatch({ type: 'ERROR', payload: { error } });
		} catch (err) {
			dispatch({ type: 'ERROR', payload: { error: String(err) } });
		}
	}, []);

	useEffect(() => {
		let c = controller.current;
		return () => {
			c.abort();
		};
	}, []);

	return useMemo(() => [triggerFetch, fetchState], [fetchState, triggerFetch]);
};

export default useLazyFetch;
