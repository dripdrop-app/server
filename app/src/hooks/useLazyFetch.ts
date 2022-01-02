import { useRef, useCallback, useEffect, useMemo, useReducer } from 'react';
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

export interface FetchState {
	error: string;
	response: AxiosResponse | null;
	data: any;
	isLoading: boolean;
	isSuccess: boolean;
	isError: boolean;
	started: boolean;
	timestamp: Date;
}

type LazyFetchFn = (config: AxiosRequestConfig) => Promise<void>;

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
			payload: { response: AxiosResponse; data: any };
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

	const triggerFetch = useCallback(async (config: AxiosRequestConfig) => {
		dispatch({ type: 'STARTED' });
		try {
			dispatch({ type: 'LOADING' });
			const response = await axios({ ...config, signal: controller.current.signal });
			let data = response.data;
			if (response.status) {
				return dispatch({ type: 'SUCCESS', payload: { response, data } });
			}
			const error = data ? (data.error ? data.error : data) : '';
			dispatch({ type: 'ERROR', payload: { error } });
		} catch (error) {
			const { response, request } = error as AxiosError;
			if (response) {
				dispatch({ type: 'ERROR', payload: { error: response.data.error || response.data } });
			} else if (request) {
				dispatch({ type: 'ERROR', payload: { error: 'No response' } });
			}
			dispatch({ type: 'ERROR', payload: { error: String(error) } });
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
