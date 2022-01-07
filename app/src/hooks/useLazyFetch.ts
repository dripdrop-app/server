import { useRef, useCallback, useEffect, useMemo, useReducer } from 'react';
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

type FetchState<T> =
	| {
			error: '';
			response: AxiosResponse<T>;
			data: T;
			isLoading: false;
			isSuccess: true;
			isError: false;
			started: true;
			timestamp: Date;
	  }
	| {
			error: string;
			response: null;
			data: null;
			isLoading: false;
			isSuccess: false;
			isError: true;
			started: true;
			timestamp: Date;
	  }
	| {
			error: '';
			response: null;
			data: null;
			isLoading: true;
			isSuccess: false;
			isError: false;
			started: true;
			timestamp: Date;
	  }
	| {
			error: '';
			response: null;
			data: null;
			isLoading: false;
			isSuccess: false;
			isError: false;
			started: true;
			timestamp: Date;
	  }
	| {
			error: '';
			response: null;
			data: null;
			isLoading: false;
			isSuccess: false;
			isError: false;
			started: false;
			timestamp: Date;
	  };

type LazyFetchFn = (config: AxiosRequestConfig) => Promise<void>;

type LazyFetch<T> = [LazyFetchFn, FetchState<T>];

type AsyncAction<T> =
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
			payload: { response: AxiosResponse<T>; data: T };
	  };

const initialState: FetchState<null> = {
	error: '',
	response: null,
	data: null,
	isLoading: false,
	isSuccess: false,
	isError: false,
	started: false,
	timestamp: new Date(Date.now()),
};

const reducer = <T>(state: FetchState<T> = initialState, action: AsyncAction<T>): FetchState<T> => {
	if (action.type === 'STARTED') {
		return {
			...initialState,
			started: true,
			timestamp: new Date(Date.now()),
		};
	} else if (action.type === 'LOADING') {
		return { ...initialState, started: true, isLoading: true };
	} else if (action.type === 'ERROR') {
		return {
			started: true,
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
			started: true,
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

const useLazyFetch = <T>(): LazyFetch<T> => {
	const [fetchState, dispatch] = useReducer(reducer, initialState);
	const controller = useRef(new AbortController());

	const triggerFetch: LazyFetchFn = useCallback(async (config: AxiosRequestConfig) => {
		dispatch({ type: 'STARTED' });
		try {
			dispatch({ type: 'LOADING' });
			const response: AxiosResponse<any> = await axios({ ...config, signal: controller.current.signal });
			return dispatch({ type: 'SUCCESS', payload: { response, data: response.data } });
		} catch (error) {
			console.log(error);
			const { response, request } = error as AxiosError;
			if (response) {
				dispatch({
					type: 'ERROR',
					payload: { error: response.data && response.data.detail ? response.data.detail : String(error) },
				});
			} else if (request) {
				dispatch({ type: 'ERROR', payload: { error: 'No response' } });
			} else {
				dispatch({ type: 'ERROR', payload: { error: String(error) } });
			}
		}
	}, []);

	useEffect(() => {
		let c = controller.current;
		return () => {
			c.abort();
		};
	}, []);

	return useMemo(() => [triggerFetch, fetchState as FetchState<T>], [fetchState, triggerFetch]);
};

export default useLazyFetch;
